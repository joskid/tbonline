"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime

from django.utils import unittest
from django.test.client import Client

from tagging.models import TaggedItem, Tag

from post.models import BasicPost, PostWithImage
from credit.models import Credit, OrderedCredit
from gallery.models import Image


def add_posts():
    posts = []
    posts.append(   BasicPost.objects.create(title='The title',
                                           slug='basicpost-1',                                                   
                                           subtitle='The subtitle',
                                           teaser='<p>The teaser</p>',
                                           introduction='<p>The introduction</p>',
                                           body='<p>The body</p>'
                                           ))

    posts.append(   BasicPost.objects.create(title='The title',
                                           slug='basicpost-2',                                                   
                                           subtitle='The subtitle',
                                           teaser='<p>The teaser</p>',
                                           introduction='<p>The introduction</p>',
                                           body='<p>The body</p>',
                                           date_published=datetime.datetime.now()+datetime.timedelta(days=1)
                                           ))

    posts.append(   BasicPost.objects.create(title='The title',
                                           slug='basicpost-3',                                                   
                                           subtitle='The subtitle',
                                           teaser='<p>The teaser</p>',
                                           introduction='<p>The introduction</p>',
                                           body='<p>The body</p>',
                                           date_published=datetime.datetime.now()
                                           ))


    image1 = Image.objects.create(title="Image title",
                                           slug='image1') 

    posts.append(   PostWithImage.objects.create(title='The title',
                                           slug='postwithimage-1',
                                           subtitle='The subtitle',
                                           teaser='<p>The teaser</p>',
                                           introduction='<p>The introduction</p>',
                                           body='<p>The body</p>',
                                           image=image1
                                           ))

    posts.append(   PostWithImage.objects.create(title='The title',
                                           slug='postwithimage-2',
                                           subtitle='The subtitle',
                                           teaser='<p>The teaser</p>',
                                           introduction='<p>The introduction</p>',
                                           body='<p>The body</p>',
                                           date_published=datetime.datetime.now()+datetime.timedelta(days=1),
                                           image=image1
                                           ))

    posts.append(   PostWithImage.objects.create(title='The title',
                                           slug='postwithimage-3',
                                           subtitle='The subtitle',
                                           teaser='<p>The teaser</p>',
                                           introduction='<p>The introduction</p>',
                                           body='<p>The body</p>',
                                           date_published=datetime.datetime.now(),
                                           image=image1
                                           ))

    return posts


def delete_posts():
    Image.objects.all().delete()
    BasicPost.objects.all().delete()

def add_tags():    
    pub = Tag.objects.create(name='published')
    unpub = Tag.objects.create(name='unpublished')
    even = Tag.objects.create(name='even')
    odd = Tag.objects.create(name='odd')

    posts = BasicPost.objects.select_subclasses()
    
    for p in posts:
        if p.is_published():
            ti = TaggedItem(object=p, tag=pub)
        else:
            ti = TaggedItem(object=p, tag=unpub)
        ti.save()
        if p.pk % 2 == 0:
            ti = TaggedItem(object=p, tag=even)
        else: 
            ti = TaggedItem(object=p, tag=odd)
        ti.save()


def delete_tags():
    Tag.objects.all().delete()

class PostTest(unittest.TestCase):

    def setUp(self):
        """
        Create some posts
        """
        self.test_posts = add_posts()
        add_tags()

    def tearDown(self):
        delete_posts()
        delete_tags()

    def testCountAllPosts(self):
        posts = BasicPost.objects.select_subclasses()
        self.assertEqual(len(posts), 6)
        
    def testCountPublishedPosts(self):
        posts = BasicPost.objects.published().select_subclasses()
        self.assertEqual(len(posts), 2)
        self.assertEqual(type(posts[0]), PostWithImage)
        self.assertEqual(type(posts[1]), BasicPost)
        self.assertEqual(posts[0].pk, 6)
        self.assertEqual(posts[1].pk, 3)

    def testCountUnpublishedPosts(self):
        posts = BasicPost.objects.unpublished().select_subclasses()
        self.assertEqual(len(posts), 4)

    def testPostPublishedListView(self):
        c = Client()
        response = c.get('/posts/')     
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['posts']),2)

    def testPostDetailView(self):
        c = Client()
        response = c.get('/posts/id/1/', follow=True)
        self.assertEquals(response.status_code, 404)
        response = c.get('/posts/id/3/', follow=True)
        self.assertEquals(response.status_code, 200)

        response = c.get('/posts/id/4/', follow=True)
        self.assertEquals(response.status_code, 404)
        response = c.get('/posts/id/6/', follow=True)
        self.assertEquals(response.status_code, 200)



    def testPostDraftView(self):

        c = Client()
        response = c.get('/posts/draft/1/', follow=True)

        # Should return 404 because user is not logged in and this post is not published
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0][0], 'http://testserver/accounts/login/?next=/posts/draft/1/')
        
        
        u = User.objects.create(username="joebloggs", email="joebloggs@example.com", is_superuser=True, is_staff=True)
        u.set_password('abcde')
        u.save()
        self.assertEquals(c.login(username='joebloggs', password='abcde'), True)

        # Should return 200 for logged in user
        response = c.get('/posts/draft/1/', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['post'].id, 1)

    def testTags(self):
        c = Client()
        response = c.get('/posts/tag/even/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['posts']), 1)
        self.assertEquals(response.context['posts'][0].id, 6)

        response = c.get('/posts/tag/published/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['posts']), 2)
        self.assertEquals(response.context['posts'][0].id, 6)
        self.assertEquals(response.context['posts'][1].id, 3)

        response = c.get('/posts/tag/unpublished/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['posts']), 0)

    def testCredits(self):
        jane = Credit.objects.create(first_names='Jane', last_name='Bloggs')
        joe = Credit.objects.create(first_names='Joe', last_name='Smith')
        lisa = Credit.objects.create(first_names='Lisa', last_name='Doe')
        tom = Credit.objects.create(first_names='Tom', last_name='Thumb')
                
        p = BasicPost.objects.filter(pk=3).select_subclasses()[0]
        o = OrderedCredit(content_object=p, credit=jane, position=3)
        o.save()
        o = OrderedCredit(content_object=p, credit=joe, position=2)
        o.save()
        o = OrderedCredit(content_object=p, credit=lisa, position=5)
        o.save()
        o = OrderedCredit(content_object=p, credit=tom, position=1)
        o.save()
                
        authors = BasicPost.objects.select_subclasses().filter(pk=3)[0].get_authors() 
        self.assertEquals(authors, "Tom Thumb, Joe Smith, Jane Bloggs and Lisa Doe")
        
        p.authors.all().delete()
        o = OrderedCredit(content_object=p, credit=lisa, position=0)
        o.save()
        authors = BasicPost.objects.select_subclasses().filter(pk=3)[0].get_authors()       
        self.assertEquals(authors, "Lisa Doe")

        p.authors.all().delete()
        o = OrderedCredit(content_object=p, credit=joe, position=1)
        o.save()        
        o = OrderedCredit(content_object=p, credit=jane, position=0)
        o.save()
        authors = BasicPost.objects.select_subclasses().filter(pk=3)[0].get_authors()        
        self.assertEquals(authors, "Jane Bloggs and Joe Smith")
        
        p.authors.all().delete()
        wikipedia = Credit.objects.create(is_person=False, 
                                          first_names="First names should be ignored", 
                                          last_name="Wikipedia")
        o = OrderedCredit(content_object=p, credit=jane, position=0)
        o.save()

        o = OrderedCredit(content_object=p, credit=wikipedia, position=1)
        o.save()
        authors = BasicPost.objects.select_subclasses().filter(pk=3)[0].get_authors()        
        self.assertEquals(authors, "Jane Bloggs and Wikipedia")
        
    def testEnhancedTextField(self):
        p = BasicPost.objects.select_subclasses()[0]
        p.teaser = "<h1>The quick brown fox jumps over the lazy dog</h1>"
        self.assertEquals(unicode(p.teaser), "<h1>The quick brown fox jumps over the lazy dog</h1>")
        p.teaser = '''
On Foxes
--------

This is a footnote text.[^EGFOOT]

[^EGFOOT]: Example footnote.
\M'''
        self.assertEquals(unicode(p.teaser), '<h2>On Foxes</h2>\n<p>This is a footnote text.<sup id="fnref:EGFOOT"><a href="#fn:EGFOOT" rel="footnote">1</a></sup></p>\n<div class="footnote">\n<hr />\n<ol>\n<li id="fn:EGFOOT">\n<p>Example footnote.\n&#160;<a href="#fnref:EGFOOT" rev="footnote" title="Jump back to footnote 1 in the text">&#8617;</a></p>\n</li>\n</ol>\n</div>')

        p.teaser = '''
TB in our ancestors
-------------------

Recent research shows that the disease probably originated at least several 
hundred thousand years ago in hominids but perhaps even more than 2 million years 
ago. [#Stone]_  

.. [#Stone] Stone *et al.* 2009. Tuberculosis and leprosy in perspective. 

\R'''
        
        self.assertEquals(unicode(p.teaser), '<p>Recent research shows that the disease probably originated at least several\nhundred thousand years ago in hominids but perhaps even more than 2 million years\nago. <a class="footnote-reference" href="#stone" id="id1">[1]</a></p>\n<table class="docutils footnote" frame="void" id="stone" rules="none">\n<colgroup><col class="label" /><col /></colgroup>\n<tbody valign="top">\n<tr><td class="label"><a class="fn-backref" href="#id1">[1]</a></td><td>Stone <em>et al.</em> 2009. Tuberculosis and leprosy in perspective.</td></tr>\n</tbody>\n</table>\n')
        
from django.contrib.auth.models import User

class AccountTest(unittest.TestCase):

    
    def setUp(self):
        User.objects.create(username="janebloggs", email="janebloggs@example.com", password="abcde")
        
    def tearDown(self):
        User.objects.all().delete()
        
    def testUser(self):
        self.assertEquals(len(User.objects.all()),1) 
        
    
    def testLogin(self):
        c = Client()      
        response = c.post('/accounts/login/', {'username': 'joebloggs@example.com', 'password': 'abcde'})
        self.assertEquals(response.status_code, 200)
        response = c.post('/accounts/logout/')
        self.assertEquals(response.status_code, 200)
        response = c.post('/accounts/login/', {'username': 'joebloggs', 'password': 'abcde'})
        self.assertEquals(response.status_code, 200)
