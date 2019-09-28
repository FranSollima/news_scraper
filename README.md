# News Scraper

En este repositorio se almacenan los scripts para realizar el scrapeado de diferentes diarios.

### Archivos:
- **news_scraper.py**: Es el script principal. Cuando se ejecuta, llama a todos los scrapers en diferentes threads (trabajan en paralelo).
	Cada scraper está encapsulado en un `while` para que se reintente indefinidamente en caso de error.
	Para que no se pierdan noticias, este script debería ejecutarse con frecuencia diaria o superior.

- **log**: Registra la acción del script (horario de comienzo, errores, número de noticias scrapeadas, tiempo de scrapeo).

- **scraper/scraper.py**: Tiene la clase `Scraper` con todas las funciones comunes de los scrapers. Incluye la creación (si no existe) del directorio de descargas: descargas/{fuente}/
	Las descargas son en formato `.json`.

- **scraper/{fuente}_scraper.py**: Tiene la clase `Scraper{fuente}` con las funciones de scrapeo específicas de la fuente. Hereda las generales de la clase `Scraper`.

#### Lista de diarios disponibles:
- Clarin
- Infobae
- La Nacion
- Página 12

#### Próximos diarios:
- Crónica
- La Izquierda Diario
