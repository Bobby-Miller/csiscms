from mezzanine.blog.models import BlogPost, BlogCategory


BlogPost._meta.verbose_name = _("Training post")
BlogPost._meta.verbose_name_plural = _("Training posts")

BlogCategory._meta.verbose_name = _("Training Category")
BlogCategory._meta.verbose_name_plural = _("Training Categories")
