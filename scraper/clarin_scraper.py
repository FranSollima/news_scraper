#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scraper import Scraper
import time

class ClarinScraper(Scraper):
	"""Aparentemente se puede bajar hacia atras ilimitadamente"""
	def __init__(self, root_dir):
		super(ClarinScraper, self).__init__(root_dir, 'clarin')

	def get_tabla_noticias(self, nro_noticias_maxima=300, limite_tiempo=20):
		# Abrimos la pagina con las ultimas noticias
		self.wd.get('https://www.clarin.com/ultimas-noticias')

		nro_noticias = len(self.wd.find_element_by_class_name('listado').find_elements_by_tag_name('article'))
		while nro_noticias < nro_noticias_maxima:
			# Agregamos mas noticias
			begin_time = time.time()
			self.wd.execute_script('window.scrollTo(0, document.body.scrollHeight)')
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
			fecha = noticia.find_element_by_class_name('fecha').text
			# Link noticia completa
			link_noticia = noticia.find_element_by_tag_name('a').get_attribute('href')
			# Si alcanzamos la ultima noticia ya cargada, interrumpimos (para no cargar duplicado)
			if link_noticia == self.ultima_noticia_descargada:
				break
			# Volanta
			volanta = ''
			if noticia.find_elements_by_class_name('volanta'):
				volanta = noticia.find_element_by_class_name('volanta').text
			# Titulo
			titulo = noticia.find_element_by_tag_name('h2').text
			# Link foto
			link_foto = ''
			if noticia.find_elements_by_tag_name('img'):
				link_foto = noticia.find_element_by_tag_name('img').get_attribute('src')
			# Resumen
			resumen = noticia.find_element_by_class_name('summary').text
			# Categorias
			categorias = [elem.text for elem in noticia.find_element_by_class_name('data-txt').find_elements_by_tag_name('p')]
			# Etiquetas
			etiquetas = [elem.text for elem in noticia.find_element_by_class_name('tags_time').find_elements_by_tag_name('a')]
			# Agregamos el diccionario con todos los datos a tabla_noticias
			tabla_noticias.append({
				'fecha_resumen': fecha,
				'link_noticia': link_noticia,
				'volanta': volanta,
				'titulo': titulo,
				'link_foto': link_foto,
				'resumen': resumen,
				'categorias': categorias,
				'etiquetas': etiquetas
			})
			# print(len(tabla_noticias))

		return tabla_noticias

	def get_cuerpo_noticia(self, noticia):
		# Abrimos la noticia
		self.wd.get(noticia['link_noticia'])

		# Si no anda el link es porque cambio, buscamos el nuevo link
		if self.wd.find_elements_by_class_name('page_404') or self.wd.current_url == 'https://www.clarin.com':
			self.wd.get('https://www.clarin.com/buscador/?q=%s' % noticia['titulo'])
			links_resultados = [elem.find_element_by_tag_name('a').get_attribute('href') for elem in self.wd.find_elements_by_class_name('gsc-thumbnail-inside')]
			max_similitud = 0
			link_nuevo = ''
			for link in links_resultados:
				similitud = max([i for i in range(len(noticia['link_noticia'])) if links_resultados[0].startswith(noticia['link_noticia'][:i])])
				if similitud > max_similitud:
					max_similitud = similitud
					link_nuevo = link

			# print('Se reemplazo el link: %s por %s' % (noticia['link_noticia'], link_nuevo))
			noticia['link_noticia'] = link_nuevo
			self.restartBrowser()
			self.wd.get(noticia['link_noticia'])

		# Si la nota no tiene cuerpo, es porque se bloqueo la pagina. Reiniciamos el browser (solo una vez)
		if self.wd.find_elements_by_xpath('//div[@class="body-nota"]/p') and not [elem.text for elem in self.wd.find_elements_by_xpath('//div[@class="body-nota"]/p') if elem.text]:
			# print('La pagina se bloqueo. Reiniciamos el browser y recargamos.')
			self.restartBrowser()
			self.wd.get(noticia['link_noticia'])

		# Fecha - hora
		fecha, hora = self.wd.find_element_by_class_name('entry-head').find_element_by_class_name('breadcrumb').text.split('\n')[0].split('-')
		fecha = fecha.strip()
		hora = hora.strip()

		# Autor
		autor = ''
		if self.wd.find_elements_by_xpath('//p[@itemprop="author"]'):
			autor = self.wd.find_element_by_xpath('//p[@itemprop="author"]').text

		# Cuerpo
		cuerpo = ''
		for bloque_texto in self.wd.find_elements_by_xpath('//div[@class="body-nota"]/p'):
			if bloque_texto.text:
				cuerpo += bloque_texto.text + '\n'

		return fecha, hora, autor, cuerpo

	def add_cuerpo_noticias(self, tabla_noticias):
		# Abrimos cada noticia y obtenemos su cuerpo
		for i in range(len(tabla_noticias)):
			# Cada cuatro noticias reiniciamos el browser
			if (i%4)==0:
				self.restartBrowser()
			# Obtenemos el cuerpo de la noticia
			fecha, hora, autor, cuerpo = self.get_cuerpo_noticia(tabla_noticias[i])
			tabla_noticias[i]['fecha'] = fecha
			tabla_noticias[i]['hora'] = hora
			tabla_noticias[i]['autor'] = autor
			tabla_noticias[i]['cuerpo'] = cuerpo
			# print(i+1)

		return tabla_noticias
