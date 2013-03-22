import mechanize
import cookielib
import datetime
from BeautifulSoup import BeautifulSoup
import soupselect

def count_rows(html):
	bs = BeautifulSoup(html)
	rows = soupselect.select(bs, 'table#searchResults tbody tr')
	print rows
	return len(rows)

def main():
	# Browser
	br = mechanize.Browser()

	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	# Want debugging messages?
	#br.set_debug_http(True)
	#br.set_debug_redirects(True)
	#br.set_debug_responses(True)

	# User-Agent (this is cheating, ok?)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

	r = br.open('http://soprweb.senate.gov/index.cfm?event=selectfields')
	for f in br.forms():
	    print f

	br.select_form(nr=0)
	br.form['searchCriteria'] = ('datePosted',)
	br.submit()

	br.select_form(nr=0)
	br.form['datePostedStart'] = '03/21/2013'
	# br.form['datePostedStart'] = datetime.datetime.now().strftime('%m/%d/%Y')	
	br.form['datePostedEnd'] = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
	br.submit()

	print "found %d registrations" % count_rows(br.response().read())

	# "Showing 1 to 100 of 398 entries"

	# # Open some site, let's pick a random one, the first that pops in mind:
	# r = br.open('http://google.com')
	# html = r.read()

	# # Show the source
	# print html
	# # or
	# print br.response().read()

	# # Show the html title
	# print br.title()

	# # Show the response headers
	# print r.info()
	# # or
	# print br.response().info()

	# # Show the available forms
	# for f in br.forms():
	#     print f

	# # Select the first (index zero) form
	# br.select_form(nr=0)

	# # Let's search
	# br.form['q']='weekend codes'
	# br.submit()
	# print br.response().read()

	# # Looking at some results in link format
	# for l in br.links(url_regex='stockrt'):
	#     print l

if __name__ == '__main__':
	main()
