# 🚀 Cómo publicar y automatizar el Monitor de Precios

Para compartir el Dashboard y que se actualice solo, la mejor opción gratuita es usar **GitHub Pages** y **GitHub Actions**.

## Pasos para publicar

1. **Crea una cuenta en GitHub** (si no tienes una).
2. **Crea un Nuevo Repositorio**:
    * Ve a [github.com/new](https://github.com/new).
    * Nombre del repositorio: `monitor-precio-europa`.
    * Crea el repositorio.

3. **Sube el código**:
    * Abre una terminal en esta carpeta (`c:\A Ideas\Antigravity\Monitor Precio Europa`).
    * Ejecuta los siguientes comandos (si tienes Git instalado):

        ```bash
        git init
        git add .
        git commit -m "Initial commit"
        git branch -M main
        git remote add origin https://github.com/Chanzes01/monitor-precio-europa.git
        git push -u origin main
        ```

4. **Activa GitHub Pages (Para ver la web)**:
    * Ve a la pestaña **Settings** de tu repositorio en GitHub.
    * En el menú izquierdo, baja hasta **Pages**.
    * En **Source**, selecciona `Deploy from a branch`.
    * En **Branch**, selecciona `main` y guarda.
    * En unos minutos, tu dashboard estará visible en: `https://Chanzes01.github.io/monitor-precio-europa/dashboard.html`

5. **Verificación de Actualización Automática**:
    * He creado un "robot" en `.github/workflows/update_data.yml`.
    * Este robot se ejecutará **todos los lunes a las 8:00 AM** para buscar nuevos precios y actualizar la web automáticamente.
    * También puedes ir a la pestaña **Actions** en GitHub y pulsar "Run workflow" para forzar una actualización manual.
