import requests
import base64
import json
from urllib.parse import unquote

def fix_b64(b64str):
    if not '=' in b64str:
        b64str += "=" * (-len(b64str) % 4)
    return b64str

def encode_id(i):
    id_base64 = base64.urlsafe_b64encode(i.encode()).decode()
    id_base64_ = id_base64.rstrip('=')
    return id_base64_

def decode_id(i):
    if 'skyflix' in i:
        i = i.replace('skyflix:', '')
    b64decode_ = fix_b64(i)
    dict_ = json.loads(base64.urlsafe_b64decode(b64decode_).decode())
    return dict_

def get_meta_tv(i):
    i_ = decode_id(i)
    try:
        iten = {
            "id": i,
            "type": "tv",
            "name": i_.get('name', ''),
            "poster": i_.get('thumb', ''),
            "background": i_.get('thumb', ''),
            "description": f"Canal {i_.get('name', '')} ao vivo.",
            "genres": [i_.get('genre', '')],
        }
        return iten
    except Exception as e:
        return {}

def get_stream_tv(i):
    i_ = decode_id(i)
    return {
        'streams': [{
        'name': 'SKYFLIX',
        'title': i_.get('name', "Live Channel"),
        'url': f"https://1playpro.alwaysdata.net/proxy?url={i_.get('stream', '')}",
        }],
    }


class xtream_api:
    def __init__(self, dns, username, password):
        self.live_categories_url = '{0}/player_api.php?username={1}&password={2}&action=get_live_categories'.format(dns, username, password)
        self.player_api = '{0}/player_api.php?username={1}&password={2}'.format(dns, username, password)
        self.play_url = '{0}/live/{1}/{2}/'.format(dns,username,password)

    def get_live_categories(self):
        try:
            response = requests.get(self.live_categories_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Safari/537.36'})
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar categorias ao vivo: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON das categorias ao vivo: {e}")
            return []

    def list_channels(self, category):
        category_mapping = {
            'Abertos': ['sbt', 'abertos', 'globo', 'record', 'band', 'redetv', 'cultura', 'tv brasil', 'aberta', 'nacional'],
            'Esportes': ['amazon', 'espn', 'sportv', 'premiere', 'esportes', 'disney', 'max', 'futebol', 'combate', 'lutas', 'velocidade', 'olimpico', 'sport tv', 'fox sports', 'band sports', 'esporte interativo'],
            'NBA': ['nba', 'basquete'],
            'PPV': ['ppv', 'pay per view'],
            'Paramount plus': ['paramount', 'paramount+'],
            'DAZN': ['dazn'],
            'Nosso Futebol': ['nosso futebol', 'futebol brasileiro'],
            'UFC': ['ufc', 'mma'],
            'Combate': ['combate', 'lutas'],
            'NFL': ['nfl', 'futebol americano'],
            'Documentarios': ['documentarios', 'documentários', 'history', 'discovery', 'nat geo', 'animal planet'],
            'Infantil': ['infantil', 'desenhos', 'kids', 'crianças', 'cartoon', 'disney channel', 'nickelodeon', 'discovery kids'],
            'Filmes e Series': ['filmes e séries', 'filmes e series', 'cinema', 'series', 'filme', 'acao', 'comedia', 'drama', 'terror', 'suspense', 'romance', 'ficcao', 'sci-fi', 'hbo', 'telecine', 'max prime', 'paramount channel', 'universal channel', 'warner channel', 'sony channel', 'fx', 'tnt', 'megapix', 'telecine premium', 'telecine action', 'telecine touch', 'telecine fun', 'telecine pipoca', 'telecine cult'],
            'Telecine': ['telecine', 'telecine premium', 'telecine action', 'telecine touch', 'telecine fun', 'telecine pipoca', 'telecine cult'],
            'HBO': ['hbo', 'hbo 2', 'hbo family', 'hbo plus', 'hbo signature', 'hbo max'],
            'Cine Sky': ['cine sky'],
            'Noticias': ['noticias', 'notícias', 'jornalismo', 'bandnews', 'globonews', 'cnn', 'record news'],
            'Musicas': ['musicas', 'músicas', 'clipe', 'mtv', 'multishow', 'bis'],
            'Variedades': ['variedades', 'entretenimento', 'lifestyle', 'gnt', 'discovery home & health', 'off', 'travel box'],
            'Cine 24h': ['cine 24h'],
            'Desenhos': ['desenhos', 'animacao', 'anime'],
            'Series 24h': ['séries 24h', 'series 24h', '24h series'],
            'Religiosos': ['religiosos', 'igreja', 'fe', 'gospel', 'catolico', 'evangelico'],
            '4K': ['4k', 'uhd', 'ultra hd'],
            'Radios': ['radios', 'radio'],
            'Reality': ['power couple', 'a fazenda', 'bbb', 'big brother', 'reality show', 'masterchef', 'de ferias com o ex'],
            'Internacionais': ['internacionais', 'internacional', 'eua', 'europa', 'asia', 'america latina'],
            'Locais': ['locais', 'regional', 'cidade'],
            'Culinaria': ['culinaria', 'gastronomia', 'comida', 'receitas', 'food network'],
            'Moda e Estilo': ['moda e estilo', 'fashion', 'beleza', 'glitz'],
            'Educativos': ['educativos', 'educacao', 'aprendizado', 'aula'],
            'Eventos': ['eventos', 'shows', 'ao vivo', 'especial'],
            'Retros': ['retros', 'classicos', 'antigos'],
            'Novelas': ['novelas', 'telenovelas'],
            'Canais de Audio': ['canais de audio', 'audio'],
            'Testes': ['testes', 'teste'],
            'Outros': ['outros', 'diversos', 'geral']
        }

        itens = []
        try:
            all_live_categories = self.get_live_categories()
            
            if all_live_categories:
                keys_to_match = category_mapping.get(category, [])
                
                if not keys_to_match and category:
                    keys_to_match = [category.lower()]

                for xtream_cat in all_live_categories:
                    xtream_cat_name = xtream_cat.get('category_name', '').lower()
                    xtream_cat_id = xtream_cat.get('category_id')

                    if not xtream_cat_id:
                        continue

                    matched = False
                    for key in keys_to_match:
                        if key in xtream_cat_name:
                            matched = True
                            break
                    
                    if category == 'All' and 'All' in xtream_cat.get('category_name', ''):
                        matched = True

                    if matched:
                        url = self.player_api + '&action=get_live_streams&category_id=' + str(xtream_cat_id)
                        i = self.channels_open(url, category)
                        if i:
                            for l in i:
                                itens.append(l)
        except Exception as e:
            print(f"Erro em list_channels: {e}")
            pass
        return itens

    def generate_id_channel(self, name, url, thumb, genre):
        i = {'name': name, 'stream': url, 'thumb': thumb, 'genre': genre}
        id_json = json.dumps(i)
        stremio_id = 'skyflix:' + encode_id(id_json)
        return stremio_id


    def channels_open(self, url, category):
        itens = []
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Safari/537.36'})
            response.raise_for_status()
            vod_cat = response.json()

            if vod_cat:
                for cat in vod_cat:
                    name = cat.get('name', '')
                    stream_id = str(cat.get('stream_id', ''))
                    url_ = '{0}{1}.m3u8'.format(self.play_url,stream_id)
                    try:
                        thumb = 'https://bsweb1-image-proxy.hf.space/proxy-image/?url=' + cat.get('stream_icon', '')
                    except:
                        thumb = ''
                    iten = {
                        "id": self.generate_id_channel(name, url_, thumb, category),
                        "type": "tv",
                        "name": name,
                        "poster": thumb,
                        "background": thumb,
                        "description": f"Canal {name} ao vivo.",
                        "genres": [category]
                    }
                    itens.append(iten)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao abrir canais: {e}")
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON dos canais: {e}")
        return itens



def get_api():
    url = 'https://bswebstrean-default-rtdb.firebaseio.com/skyflix.json'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Safari/537.36'})
        response.raise_for_status()
        data = response.json()
        api = xtream_api(data['host'], data['username'], data['password'])
        return api
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'Erro ao buscar dados da API do Firebase: {e}')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'Erro ao decodificar JSON do Firebase: {e}')
    except KeyError as e:
        raise RuntimeError(f'Dados de API incompletos do Firebase: {e}')
