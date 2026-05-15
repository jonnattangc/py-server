from app import create_app


class TestFactory:
    def test_create_app_returns_flask_app(self, app):
        from flask import Flask
        assert isinstance(app, Flask)

    def test_app_has_swagger_registered(self, app):
        assert "SWAGGER" in app.config

    def test_app_has_blueprints(self, app):
        # At least some of our blueprints should be registered
        names = [bp.name for bp in app.blueprints.values()]
        assert "main" in names
        assert "check" in names
        assert "status" in names

    def test_app_config(self, app):
        assert app.config["DEBUG"] is False
        assert app.config["SECRET_KEY"] is not None

    def test_app_routes_exist(self, app):
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert "/" in rules
        assert "/apidocs/" in rules or "/apidocs" in rules
        assert "/infojonna" in rules
        assert "/status" in rules
        assert "/checkall" in rules
