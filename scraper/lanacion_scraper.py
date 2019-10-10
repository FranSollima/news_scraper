#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .scraper import Scraper
import time

class LaNacionScraper(Scraper):
	"""Aparentemente se puede bajar hacia atras hasta 24 horas"""
	def __init__(self, root_dir):
		super(LaNacionScraper, self).__init__(root_dir, 'la nacion')

	def get_tabla_noticias(self, limite_tiempo=20):
		# Abrimos la pagina con las ultimas noticias
		self.wd.get('https://www.lanacion.com.ar/ultimas-noticias')

		while self.wd.find_element_by_id('verMas').is_displayed():
			# Agregamos mas noticias
			begin_time = time.time()
			nro_noticias = len(self.wd.find_element_by_class_name('listado').find_elements_by_tag_name('article'))
			self.wd.execute_script('window.scrollTo(0, document.body.scrollHeight);document.getElementById("verMas").click();')
			# Esperamos a que se carguen mas noticias
			while len(self.wd.find_element_by_class_name('listado').find_elements_by_tag_name('article')) <= nro_noticias:
				# Si pasa demasiado tiempo, se trabo la pagina. Reiniciamos el browser
				if time.time() - begin_time > limite_tiempo:
					# print('Timeout error intentando obtener la lista de noticias. Reiniciamos el Browser.')
					return False
			# Vemos las noticias presentes en la pagina
			noticias_cargadas_en_browser = self.wd.find_element_by_class_name('listado').find_elements_by_tag_name('article')
			nro_noticias = len(noticias_cargadas_en_browser)
			# print(nro_noticias)
			# Si ya aparecio la ultima noticia bajada, cargamos hasta ahi
			links_noticias_cargadas_en_browser = [elem.find_element_by_tag_name('a').get_attribute('href') for elem in noticias_cargadas_en_browser]
			if self.ultima_noticia_descargada in links_noticias_cargadas_en_browser:
				break

		# Obtenemos los links y los datos basicos de las noticias cargadas
		tabla_noticias = []
		for noticia in self.wd.find_element_by_class_name('listado').find_elements_by_tag_name('article'):
			# Fecha
			fecha = noticia.find_element_by_class_name('hora').text
			# Link noticia completa
			link_noticia = noticia.find_element_by_tag_name('a').get_attribute('href')
			# Si alcanzamos la ultima noticia ya cargada, interrumpimos (para no cargar duplicado)
			if link_noticia == self.ultima_noticia_descargada:
				break
			# Titulo
			titulo = noticia.find_element_by_tag_name('h2').text
			# Link foto
			link_foto = ''
			if noticia.find_elements_by_tag_name('img'):
				link_foto = noticia.find_element_by_tag_name('img').get_attribute('src')
			# Agregamos el diccionario con todos los datos a tabla_noticias
			tabla_noticias.append({
				'fecha_resumen': fecha,
				'link_noticia': link_noticia,
				'volanta': '',
				'titulo': titulo,
				'link_foto': link_foto,
				'resumen': ''
			})
			# print(len(tabla_noticias))

		return tabla_noticias

	def get_cuerpo_noticia(self, noticia):
		# Meses
		meses = {
			'enero': '01',
			'febrero': '02',
			'marzo': '03',
			'abril': '04',
			'mayo': '05',
			'junio': '06',
			'julio': '07',
			'agosto': '08',
			'septiembre': '09',
			'octubre': '10',
			'noviembre': '11',
			'diciembre': '12',
		}

		# Abrimos la noticia
		self.wd.get(noticia['link_noticia'])

		# Si la nota no tiene cuerpo, es porque se bloqueo la pagina. Reiniciamos el browser (solo una vez)
		if not self.wd.find_elements_by_xpath('//section[@id="cuerpo"]/p'):
			# print('La pagina se bloqueo. Reiniciamos el browser y recargamos.')
			self.restartBrowser()
			self.wd.get(noticia['link_noticia'])

		# Fecha - hora
		datos_fecha_hora = self.wd.find_element_by_class_name('fecha').text.split(' ')
		if len(datos_fecha_hora) > 7:
			dia, mes, anio, hora = datos_fecha_hora[0], datos_fecha_hora[2], datos_fecha_hora[4], datos_fecha_hora[7]
		else:
			dia, mes, anio, hora = datos_fecha_hora[0], datos_fecha_hora[2], datos_fecha_hora[4], ''
		fecha = '%s/%s/%s' % (dia, meses[mes], anio)

		# Categoria
		categoria = ''
		if self.wd.find_elements_by_class_name('categoria'):
			categoria = self.wd.find_element_by_class_name('categoria').text

		# Etiqueta
		etiqueta = ''
		if self.wd.find_elements_by_class_name('tag'):
			etiqueta = self.wd.find_element_by_class_name('tag').text

		# Autor
		autor = ''
		if self.wd.find_elements_by_class_name('autor'):
			autor = self.wd.find_element_by_class_name('autor').find_element_by_tag_name('a').text

		# Cuerpo
		cuerpo = ''
		for bloque_texto in self.wd.find_elements_by_xpath('//section[@id="cuerpo"]/p'):
			if bloque_texto.text:
				cuerpo += bloque_texto.text + '\n'

		return fecha, hora, categoria, etiqueta, autor, cuerpo

	def add_cuerpo_noticias(self, tabla_noticias):
		# Abrimos cada noticia y obtenemos su cuerpo
		for i in range(len(tabla_noticias)):
			# Cada cuatro noticias reiniciamos el browser
			if (i%15)==0:
				self.restartBrowser()
			# Obtenemos el cuerpo de la noticia
			try:
				fecha, hora, categoria, etiqueta, autor, cuerpo = self.get_cuerpo_noticia(tabla_noticias[i])
			except Exception as e:
				raise e
				# import ipdb; ipdb.set_trace()
			tabla_noticias[i]['fecha'] = fecha
			tabla_noticias[i]['hora'] = hora
			tabla_noticias[i]['categoria'] = categoria
			tabla_noticias[i]['etiqueta'] = etiqueta
			tabla_noticias[i]['autor'] = autor
			tabla_noticias[i]['cuerpo'] = cuerpo
			# print(i+1)

		return tabla_noticias
