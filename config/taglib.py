from google.appengine.ext import webapp

register = webapp.template.create_template_register()

def sampleTag(value):
    return " SAMPLED LIKE A BITCH"

register.filter(sampleTag)