from scraper import Scraper
import time

class InfobaeScraper(Scraper):
	"""Aparentemente se puede bajar hacia atras ilimitadamente"""
	def __init__(self, root_dir):
		super(InfobaeScraper, self).__init__(root_dir, 'infobae')

	def get_tabla_noticias(self, nro_noticias_maxima=300, limite_tiempo=20):
		# Abrimos la pagina con las ultimas noticias
		self.wd.get('https://www.infobae.com/ultimas-noticias/')

		nro_noticias = len(self.wd.find_element_by_class_name('result-listing').find_elements_by_tag_name('article'))
		while nro_noticias < nro_noticias_maxima:
			# Agregamos mas noticias
			begin_time = time.time()
			self.wd.execute_script('window.scrollTo(0, document.body.scrollHeight);document.getElementsByClassName("pb-loadmore")[0].click();')
			# Esperamos a que se carguen mas noticias
			while len(self.wd.find_element_by_class_name('result-listing').find_elements_by_tag_name('article')) <= nro_noticias:
				# Si pasa demasiado tiempo, se trabo la pagina. Reiniciamos el browser
				if time.time() - begin_time > limite_tiempo:
					print('Timeout error intentando obtener la lista de noticias. Reiniciamos el Browser.')
					return False
			# Vemos las noticias presentes en la pagina
			noticias_cargadas_en_browser = self.wd.find_element_by_class_name('result-listing').find_elements_by_tag_name('article')
			nro_noticias = len(noticias_cargadas_en_browser)
			print(nro_noticias)
			# Si ya aparecio la ultima noticia bajada, cargamos hasta ahi
			links_noticias_cargadas_en_browser = [elem.find_element_by_tag_name('a').get_attribute('href') for elem in noticias_cargadas_en_browser]
			if self.ultima_noticia_descargada in links_noticias_cargadas_en_browser:
				break

		# Obtenemos los links y los datos basicos de las noticias cargadas
		tabla_noticias = []
		for noticia in self.wd.find_element_by_class_name('result-listing').find_elements_by_tag_name('article'):
			# Fecha
			fecha = noticia.find_element_by_tag_name('time').text
			# Link noticia completa
			link_noticia = noticia.find_element_by_tag_name('a').get_attribute('href')
			# Si alcanzamos la ultima noticia ya cargada, interrumpimos (para no cargar duplicado)
			if link_noticia == self.ultima_noticia_descargada:
				break
			# Titulo
			titulo = noticia.find_element_by_tag_name('h4').text
			# Link foto
			link_foto = ''
			if noticia.find_elements_by_tag_name('img'):
				link_foto = noticia.find_element_by_tag_name('img').get_attribute('src')
			# Resumen
			resumen = noticia.find_element_by_class_name('excerpt').text
			# Agregamos el diccionario con todos los datos a tabla_noticias
			tabla_noticias.append({
				'fecha_resumen': fecha,
				'link_noticia': link_noticia,
				'volanta': '',
				'titulo': titulo,
				'link_foto': link_foto,
				'resumen': resumen,
				'etiquetas': []
			})
			print(len(tabla_noticias))

		return tabla_noticias

	def get_cuerpo_noticia(self, noticia):
		try:
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

			# Si no encontro la noticia, la salteamos
			if self.wd.current_url == 'https://www.infobae.com/' or self.wd.title.upper() == 'HACEMOS PERIODISMO - INFOBAE':
				return '', '', [], '', '', ''

			# Fecha - hora
			datos_fecha = self.wd.find_element_by_class_name('byline-date').text.strip().split(' ')
			dia, mes, anio = datos_fecha[0], datos_fecha[2], datos_fecha[4]
			fecha = '%s/%s/%s' % (dia, meses[mes], anio)
			hora = ''

			# Categoria
			categoria = []
			if self.wd.find_element_by_class_name('article-header').find_elements_by_class_name('header-label'):
				categoria = [self.wd.find_element_by_class_name('article-header').find_element_by_class_name('header-label').text]

			# Resumen
			resumen = ''
			if self.wd.find_elements_by_class_name('subheadline'):
				resumen = self.wd.find_element_by_class_name('subheadline').text

			# Autor
			autor = ''
			if self.wd.find_elements_by_class_name('author-name'):
				autor = self.wd.find_element_by_class_name('author-name').text

			# Cuerpo
			cuerpo = ''
			for bloque_texto in self.wd.find_elements_by_class_name('element-paragraph'):
				# Detectamos el final del cuerpo
				if bloque_texto.text and bloque_texto.text == 'SIGA LEYENDO':
					break

				if bloque_texto.text:
					cuerpo += bloque_texto.text + '\n'

			return fecha, hora, categoria, resumen, autor, cuerpo
		except:
			import ipdb; ipdb.set_trace()

	def add_cuerpo_noticias(self, tabla_noticias):
		# Abrimos cada noticia y obtenemos su cuerpo
		for i in range(len(tabla_noticias)):
			# Obtenemos el cuerpo de la noticia
			try:
				fecha, hora, categoria, resumen, autor, cuerpo = self.get_cuerpo_noticia(tabla_noticias[i])
				tabla_noticias[i]['fecha'] = fecha
				tabla_noticias[i]['hora'] = hora
				tabla_noticias[i]['categoria'] = categoria
				tabla_noticias[i]['resumen'] = resumen
				tabla_noticias[i]['autor'] = autor
				tabla_noticias[i]['cuerpo'] = cuerpo
			except:
				import ipdb; ipdb.set_trace()
			print(i+1)

		return tabla_noticias
