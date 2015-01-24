from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
import string

def CreateNewPost(title, content):
	wp = Client('your blog url'+'/xmlrpc.php', 'username', 'password')
	post = WordPressPost()
	post.title = title
	post.content = content
	post.post_status = 'publish'
	
	tagsCategories = [word.strip(string.punctuation) for word in title.split() if word.strip(string.punctuation)!='']
	
	print tagsCategories
	
	post.terms_names = {
		'post_tag' : tagsCategories,
		'category' : tagsCategories
	}
	
	wp.call(NewPost(post))
