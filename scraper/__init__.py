from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import json
import os
import time

class Scraper():
	"""Estructura basica del scraper"""
	def __init__(self, root_dir, fuente):
		# Nombre del scraper
		self.fuente = fuente.capitalize()
		self.nombre = 'Scraper - %s' % self.fuente
		# Abrimos el browser
		self.startBrowser()
		# Guardamos el path del archivo de salida
		self.path_descargas = os.path.join(root_dir, 'descargas', fuente.replace(' ', '').lower())
		if not os.path.exists(self.path_descargas):
			os.makedirs(self.path_descargas)
		self.path_json_salida = os.path.join(self.path_descargas, '%s - noticias.json' % time.strftime('%Y-%m-%d %H:%M'))
		# Obtenemos la ultima noticia descargada
		self.ultima_noticia_descargada = self.get_link_ultima_noticia()

	def startBrowser(self):
		self.wd = self.openChrome()
		self.wd.maximize_window()

	def restartBrowser(self):
		self.wd.quit()
		self.startBrowser()

	def openChrome(self, headless=True):
		# Abrimos el navegador
		if not headless:
			return webdriver.Chrome()
		options = Options()
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		return webdriver.Chrome(chrome_options=options)

	def get_link_ultima_noticia(self):
		# Buscamos el link de la ultima nota descargada
		try:
			ultimo_json = self.path_descargas+sorted(os.listdir(self.path_descargas), reverse=True)[0]
		except IndexError:
			return 'No hay nada descargado.'
		with open(ultimo_json) as f:
			ultima_noticia = json.load(f)[0]['link_noticia']
		return ultima_noticia

	def save_json_noticias(self, tabla_noticias):
		with open(self.path_json_salida, 'w') as f:
			json.dump(tabla_noticias, f)

	def scrape(self):
		# Tiempo de inicio
		begin_time = time.time()

		# Obtenemos las ultimas noticias, con sus datos basicos
		tabla_noticias = False
		while not tabla_noticias:
			print('Intentamos obtener la lista de noticias')
			tabla_noticias = self.get_tabla_noticias()
			self.restartBrowser()  # Nuevo browser

		# Otenemos el cuerpo de las noticias obtenidas
		print('Obtenemos los datos de las noticias')
		tabla_noticias = self.add_cuerpo_noticias(tabla_noticias)

		# Bajamos los datos a un archivo json
		self.save_json_noticias(tabla_noticias)

		# Tiempo de finalizacion
		end_time = time.time()

		return {'fuente': self.fuente, 'nro_noticias': len(tabla_noticias), 'tiempo': end_time-begin_time, 'archivo_salida': self.path_json_salida}
