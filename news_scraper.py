# Scrapers
from scraper.clarin_scraper import ClarinScraper
from scraper.lanacion_scraper import LaNacionScraper
from scraper.infobae_scraper import InfobaeScraper
from scraper.pagina12_scraper import Pagina12Scraper

# Genericas
from threading import Thread
import os
import sys
root_dir = sys.argv[0].rpartition('/')[0]

def printlog(texto):
	with open(os.path.join(root_dir, 'log'), 'a') as f:
		print(texto)
		f.write(texto+'\n')

def printlog_resultados(resultados):
	tiempo_seg = int(round(resultados['tiempo']))
	tiempo_alt = ''
	if tiempo_seg > 7200:
		tiempo_alt = ' (~%shs)' % str(round(tiempo_seg/3600.0, 2)).replace('.', ',')
	elif tiempo_seg > 120:
		tiempo_alt = ' (~%imin)' % int(round(tiempo_seg/60.0))

	texto_resultados = '''
Se scrapearon las ultimas {nro_noticias} noticias de la web de {fuente}.
Se guardo lo scrapeado en el archivo {archivo_salida}.
El proceso tardo {tiempo_seg} segundos{tiempo_alt}.
'''.format(tiempo_seg=tiempo_seg, tiempo_alt=tiempo_alt, **resultados)

	printlog(texto_resultados)

def ejecuta_scraper(scraper):
	# Cada ejecucion se repite hasta que termine sin error, como maximo max_retries
	max_retries = 10
	retries = 0
	while retries < max_retries:
		try:
			s = scraper(root_dir)
			printlog('\n%s: Comienza ejecucion' % s.nombre)
			resultados = s.scrape()
			printlog_resultados(resultados)
			break
		except Exception as e:
			retries += 1
			printlog('Error ejecutando %s: %s' % (str(scraper), str(e)))
			printlog(str(e.args))

if __name__ == '__main__':
	printlog('-------------------------------------------------------------------------')
	lista_scrapers = (ClarinScraper, LaNacionScraper, InfobaeScraper, Pagina12Scraper)
	if len(sys.argv) > 1:
		scraper_solicitado = sys.argv[1]
		if scraper_solicitado == 'clarin':
			lista_scrapers = (ClarinScraper, )
		elif scraper_solicitado == 'lanacion':
			lista_scrapers = (LaNacionScraper, )
		elif scraper_solicitado == 'infobae':
			lista_scrapers = (InfobaeScraper, )
		elif scraper_solicitado == 'pagina12':
			lista_scrapers = (Pagina12Scraper, )
	for scraper in lista_scrapers:
		thread = Thread(target=ejecuta_scraper, args=(scraper,))
		thread.start()
