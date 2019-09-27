# Scrapers
from scraper.clarin_scraper import ClarinScraper
from scraper.lanacion_scraper import LaNacionScraper
from scraper.infobae_scraper import InfobaeScraper

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
	# Cada ejecucion se repite hasta que termine sin error
	while True:
		try:
			s = scraper(root_dir)
			printlog('\n%s: Comienza ejecucion' % s.nombre)
			resultados = s.scrape()
			printlog_resultados(resultados)
			break
		except Exception, e:
			printlog('Error ejecutando %s: %s' % (s.nombre, str(e)))

if __name__ == '__main__':
	printlog('-------------------------------------------------------------------------')
	for scraper in (ClarinScraper, LaNacionScraper, InfobaeScraper):
		thread = Thread(target=ejecuta_scraper, args=(scraper,))
		thread.start()
