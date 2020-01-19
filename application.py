from flask import Flask

from rssbriefing_package import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
