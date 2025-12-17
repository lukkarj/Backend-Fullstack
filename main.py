from app import create_app

# ======================================================
# Entrada do aplicativo
# ======================================================

# Cria o aplicativo
app = create_app()

# Roda o aplicativo
if __name__ == "__main__":
    app.run(debug=True)