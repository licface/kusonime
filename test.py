# import os
# pid = os.getpid()
# print "PID: ", pid
# class TEST(object):
# 	def __init__(self):
# 		self.data1 = None
# 		self.data2 = "ADA"

# 	def get_data(self):
# 		t = hasattr(self, "data2")
# 		print "t =", t

import neonime
import sys
from pprint import pprint
c = neonime.Neonime()
home = c.home(set_attrs=True)
print "HOME 1 =", c.update_anime
print "-"*220
print "HOME 2 =", c.new_anime
print "-"*220
print "HOME 3 =", c.new_movies
print "-"*220

# pages = c.paginator()
# print "pages =", pages
# url = pages.get(2)[1].get('next_page')
# url = pages.get(1)[1].get('next_page')
# url = pages.get(3)[1].get('next_page')
# print "url =", url
# c.home(url, search=True, debugx=True)
# c.get_new_anime(url=url, debugx=True)
# c.get_update_anime_perpage(url=url, debugx=True)
# c.navigator(home_url=url, debugx=True)
# c.get_new_anime(url=url, debugx=True)
# c.search(sys.argv[1])

# data = c.get_anime_details('https://neonime.net/episode/kemurikusa-tv-1x1/')
# data = c.get_anime_details('https://neonime.net/episode/tsurune-kazemai-koukou-kyuudoubu-1x11-2/')
# data = c.get_new_anime_details('https://neonime.net/tvshows/hero-mask-subtitle-indonesia/')
# data = c.get_movie_details('https://neonime.net/mob-psycho-100-reigen-shirarezaru-kiseki-no-reinouryokusha-subtitle-indonesia/')
# for i in data:
# 	print i
# 	print "-"*200

# pprint(data[2])

# c.home()
# c.get_movie_details()
# c.get_movie_details('https://neonime.net/mob-psycho-100-reigen-shirarezaru-kiseki-no-reinouryokusha-subtitle-indonesia/')
# print c.setHeaders()

# if __name__ == '__main__':
	# c = TEST()
	# c.get_data()