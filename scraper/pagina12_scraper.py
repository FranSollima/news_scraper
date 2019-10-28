#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .scraper import Scraper
import datetime

class Pagina12Scraper(Scraper):
	"""Aparentemente se puede bajar hacia atras ilimitadamente"""
	def __init__(self, root_dir):
		super(Pagina12Scraper, self).__init__(root_dir, 'pagina12')

	def parsea_fecha(self, fecha_texto):
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

		datos_fecha = fecha_texto.split()
		dia, mes, anio = datos_fecha[0], datos_fecha[2], datos_fecha[4]

		return '%s/%s/%s' % (dia, meses[mes], anio)

	def get_tabla_noticias(self):
		# Abrimos la pagina principal
		self.wd.get('https://www.pagina12.com.ar/')

		# Obtenemos los links de las categorias
		lista_categorias = self.wd.find_element_by_class_name('main-menu').find_element_by_class_name('sections').find_elements_by_tag_name('li')
		links_categorias = [elem.find_element_by_tag_name('a').get_attribute('href') for elem in lista_categorias]
		# Dejamos solo links de "secciones"
		links_categorias = [elem for elem in links_categorias if '/secciones/' in elem]

		# Para cada categoria, buscamos los articulos
		tabla_noticias = []
		for link_cat in links_categorias:
			tabla_noticias = self.get_noticias_categoria(link_cat, tabla_noticias)

		return tabla_noticias

	def get_noticias_categoria(self, link_cat, tabla_noticias):
		# Fecha de ayer
		# fecha_ayer = datetime.datetime.now() - datetime.timedelta(1)
		fecha_ayer = datetime.datetime.now()
		fecha_ayer = fecha_ayer.replace(hour=0, minute=0, second=0, microsecond=0)

		# Obtenemos las noticias de esa categoria, como maximo los articulos de los ultimos dos dias (lo que haya del actual + el anterior completo)
		self.wd.get(link_cat)

		# Nombre categoria
		categoria = self.wd.find_element_by_class_name('main-title-1').text
		# print(categoria)  # Esto tira tremendo error en el crontab!!! SOLO PARA DEBUGGING!

		# Si no hay noticias en la pagina, interrumpimos
		if not self.wd.find_elements_by_class_name('featured-article-sections')+self.wd.find_elements_by_class_name('article-box-sections'):
			return tabla_noticias

		# Hasta alcanzar el dia ante-anterior, cargamos
		while True:
			# Cargamos las noticias de la pagina actual
			for noticia in self.wd.find_elements_by_class_name('featured-article-sections')+self.wd.find_elements_by_class_name('article-box-sections'):
				# Fecha
				fecha = self.parsea_fecha(noticia.find_element_by_class_name('date-1').text)
				# Si llegamos al dia ante-anterior, interrumpimos
				if datetime.datetime.strptime(fecha, '%d/%m/%Y') < fecha_ayer:
					return tabla_noticias
				# Link noticia completa
				link_noticia = noticia.find_element_by_tag_name('a').get_attribute('href')
				# Si alcanzamos una noticia ya cargada, interrumpimos (para no cargar duplicado)
				if link_noticia in [elem['link_noticia'] for elem in self.ultima_tabla_noticias_descargada]:
					return tabla_noticias
				# Link foto
				link_foto = ''
				try:
					link_foto = [elem.get_attribute('src') for elem in noticia.find_elements_by_tag_name('img') if elem.get_attribute('src')][0]
				except IndexError:
					pass
				# Titulo
				titulo = noticia.find_element_by_tag_name('h2').text
				# Resumen
				resumen = ''
				if noticia.find_elements_by_class_name('subhead'):
					resumen = noticia.find_element_by_class_name('subhead').text
				# Agregamos el diccionario con todos los datos a tabla_noticias
				tabla_noticias.append({
					'fecha_resumen': fecha,
					'link_noticia': link_noticia,
					'volanta': '',
					'titulo': titulo,
					'link_foto': link_foto,
					'resumen': resumen,
					'categorias': [categoria],
					'etiquetas': []
				})
			# Si no se puede pasar a la proxima pagina, terminamos
			if not self.wd.find_elements_by_class_name('pagination-btn-next'):
				return tabla_noticias
			# Pasamos a la proxima pagina
			self.wd.execute_script('document.getElementsByClassName("pagination-btn-next")[0].click()')
		return tabla_noticias

	def get_cuerpo_noticia(self, noticia):
		try:
			# Abrimos la noticia
			self.wd.get(noticia['link_noticia'])

			articulo = self.wd.find_element_by_class_name('article-inner')

			# Fecha - hora
			anio, mes, dia = articulo.find_element_by_class_name('time').find_element_by_tag_name('span').get_attribute('datetime').split('-')
			fecha = '%s/%s/%s' % (dia, mes, anio)
			hora = ''

			# Volanta
			volanta = ''
			if articulo.find_elements_by_class_name('article-prefix'):
				volanta = articulo.find_element_by_class_name('article-prefix').text

			# Resumen
			resumen = ''
			if articulo.find_elements_by_class_name('article-summary'):
				resumen = articulo.find_element_by_class_name('article-summary').text

			# Autor
			autor = ''
			if articulo.find_elements_by_class_name('article-author'):
				autor = articulo.find_element_by_class_name('article-author').find_element_by_tag_name('a').text

			# Cuerpo
			cuerpo = ''
			for bloque_texto in articulo.find_element_by_class_name('article-text').find_elements_by_tag_name('p'):
				if bloque_texto.text:
					cuerpo += bloque_texto.text + '\n'

			return fecha, hora, volanta, resumen, autor, cuerpo
		except Exception as e:
			raise e
			# import ipdb; ipdb.set_trace()

	def add_cuerpo_noticias(self, tabla_noticias):
		# Abrimos cada noticia y obtenemos su cuerpo
		# print(len(tabla_noticias))
		for i in range(len(tabla_noticias)):
			# Obtenemos el cuerpo de la noticia
			try:
				fecha, hora, volanta, resumen, autor, cuerpo = self.get_cuerpo_noticia(tabla_noticias[i])
				tabla_noticias[i]['fecha'] = fecha
				tabla_noticias[i]['hora'] = hora
				tabla_noticias[i]['volanta'] = volanta
				tabla_noticias[i]['resumen'] = resumen
				tabla_noticias[i]['autor'] = autor
				tabla_noticias[i]['cuerpo'] = cuerpo
			except Exception as e:
				raise e
				# import ipdb; ipdb.set_trace()
			# print(i+1)

		return tabla_noticias
