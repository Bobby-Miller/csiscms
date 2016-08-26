from mezzanine.blog.models import BlogPost, BlogCategory


BlogPost._meta.verbose_name = "Training post"
BlogPost._meta.verbose_name_plural = "Training posts"

BlogCategory._meta.verbose_name = "Training Category"
BlogCategory._meta.verbose_name_plural = "Training Categories"
