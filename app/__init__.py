"""Async Quart application factory"""
import os
import logging
from quart import Quart
from .extensions import init_async_db, auth_manager, init_cors, cache, csrf
from config import get_config


def validate_production_config(app):
    """Fail fast on missing critical settings in production."""
    if app.config.get('DEBUG'):
        return

    errors = []
    warnings = []

    if not app.config.get('SECRET_KEY'):
        errors.append('SECRET_KEY')

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if db_uri.startswith('sqlite'):
        warnings.append('Using sqlite in production; not recommended for multi-instance deployments')
    if not app.config.get('USE_SQLITE') and not os.environ.get('DATABASE_URL'):
        errors.append('DATABASE_URL (required for production)')

    if app.config.get('DISABLE_EMAIL_VERIFICATION', False):
        errors.append('DISABLE_EMAIL_VERIFICATION must be false in production')
    else:
        email_method = app.config.get('EMAIL_METHOD', 'smtp')
        if email_method not in {'smtp', 'resend', 'local_api'}:
            errors.append('EMAIL_METHOD must be smtp, resend, or local_api')

        if not app.config.get('MAIL_DEFAULT_SENDER'):
            errors.append('MAIL_DEFAULT_SENDER')

        if email_method == 'smtp':
            if not app.config.get('MAIL_SERVER'):
                errors.append('MAIL_SERVER')
            has_user = bool(app.config.get('MAIL_USERNAME'))
            has_pass = bool(app.config.get('MAIL_PASSWORD'))
            if has_user != has_pass:
                errors.append('MAIL_USERNAME and MAIL_PASSWORD (both required if using auth)')
            if not has_user and not has_pass:
                warnings.append('SMTP auth not configured; ensure your SMTP server allows unauthenticated send')
        elif email_method == 'resend':
            if not app.config.get('RESEND_API_KEY'):
                errors.append('RESEND_API_KEY')
        elif email_method == 'local_api':
            if not app.config.get('LOCAL_MAIL_API_URL') or not app.config.get('LOCAL_MAIL_API_KEY'):
                errors.append('LOCAL_MAIL_API_URL and LOCAL_MAIL_API_KEY')

    if app.config.get('PREFERRED_URL_SCHEME') != 'https':
        warnings.append('PREFERRED_URL_SCHEME should be https in production')

    if not app.config.get('SERVER_NAME'):
        warnings.append('SERVER_NAME not set; confirmation links will use the incoming request host')

    if errors:
        raise RuntimeError(
            "Production config missing/invalid: " + "; ".join(sorted(set(errors)))
        )

    for warning in warnings:
        app.logger.warning(f"PROD CONFIG: {warning}")


def create_app():
    """Create and configure the Quart application."""
    app = Quart(
        __name__,
        instance_relative_config=True,
        template_folder='../templates',
        static_folder='../static'
    )

    app.config.from_object(get_config())
    os.makedirs(app.instance_path, exist_ok=True)

    # Cloudinary
    if app.config.get('STORAGE_BACKEND') == 'cloudinary':
        import cloudinary
        if (app.config.get('CLOUDINARY_CLOUD_NAME') and
                app.config.get('CLOUDINARY_API_KEY') and
                app.config.get('CLOUDINARY_API_SECRET')):
            cloudinary.config(
                cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
                api_key=app.config['CLOUDINARY_API_KEY'],
                api_secret=app.config['CLOUDINARY_API_SECRET'],
                secure=True
            )
            app.logger.info("Cloudinary configured.")

    logging.basicConfig(level=logging.DEBUG if app.config['DEBUG'] else logging.WARNING)
    app.logger.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.WARNING)

    validate_production_config(app)

    # Better Stack
    if app.config.get('USE_BETTERSTACK') and app.config.get('BETTERSTACK_SOURCE_TOKEN'):
        try:
            from logtail import LogtailHandler
            handler = LogtailHandler(
                source_token=app.config['BETTERSTACK_SOURCE_TOKEN'],
                host=app.config.get('BETTERSTACK_HOST', 'https://in.logs.betterstack.com')
            )
            app.logger.addHandler(handler)
            app.logger.info("Better Stack logging enabled")
        except Exception as e:
            app.logger.warning(f"Failed to setup Better Stack: {e}")
    
    init_async_db(app)
    auth_manager.init_app(app)
    csrf.init_app(app)
    init_cors(app)

    try:
        from .providers import init_providers
        init_providers(app)
    except Exception as e:
        app.logger.warning(f"Could not initialize providers: {e}")

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.manifest import manifest_bp
    from .routes.subtitles import subtitles_bp
    from .routes.content import content_bp
    from .routes.providers import providers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(manifest_bp)
    app.register_blueprint(subtitles_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(providers_bp)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.context_processor
    def inject_providers():
        try:
            from .providers.registry import ProviderRegistry
            return {
                'get_all_providers': ProviderRegistry.get_all,
                'get_provider': ProviderRegistry.get
            }
        except:
            return {
                'get_all_providers': lambda: [],
                'get_provider': lambda x: None
            }
    
    @app.context_processor
    async def inject_user():
        from quart_auth import current_user
        try:
            is_auth = await current_user.is_authenticated
        except:
            is_auth = False
        
        if is_auth:
            from .models import User
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            from .extensions import async_session_maker
            async with async_session_maker() as session:
                result = await session.execute(
                    select(User)
                    .filter_by(id=current_user.auth_id)
                    .options(
                        selectinload(User.uploaded_subtitles),
                        selectinload(User.selections),
                        selectinload(User.votes)
                    )
                )
                user = result.scalar_one_or_none()
                if user:
                    # Access relationships to load them before session closes
                    _ = user.uploaded_subtitles
                    _ = user.selections
                    _ = user.votes
                    return {'user': user}
        return {'user': None}

    return app
