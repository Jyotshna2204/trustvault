from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True is for local development only. We turn it off when deploying.
    app.run(debug=True)