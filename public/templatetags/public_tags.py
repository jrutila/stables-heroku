from django import template
register = template.Library()

from cms.utils.page_resolver import get_page_from_path
@register.inclusion_tag('public/features_list.html', takes_context=True)
def get_features(context):
    context['root'] = get_page_from_path('features')
    if context['root'] and context['root'].children.filter(published=True):
        context['features'] = context['root'].children.filter(published=True)
        for f in context['features']:
            setattr(f, 'plchld', {})
            for p in f.placeholders.all():
                f.plchld[p.slot] = p
    return context

@register.inclusion_tag('public/pricing_list.html', takes_context=True)
def get_pricings(context):
    context['root'] = get_page_from_path('pricing')
    if context['root'] and context['root'].children.filter(published=True):
        context['pricings'] = context['root'].children.filter(published=True)
        for f in context['pricings']:
            setattr(f, 'plchld', {})
            for p in f.placeholders.all():
                f.plchld[p.slot] = p
    return context

@register.inclusion_tag('public/_features.html', takes_context=True)
def render_feature(context):
    context['root'] = get_page_from_path('features')
    return context

@register.inclusion_tag('public/frontpage_slider.html', takes_context=True)
def get_slider(context):
    context['root'] = get_page_from_path('slider')
    if context['root'] and context['root'].children.filter(published=True):
        context['slides'] = context['root'].children.filter(published=True)
        for s in context['slides']:
            setattr(s, 'plchld', {})
            for p in s.placeholders.all():
                if p.slot == 'background':
                    setattr(s, 'background', p.get_plugins()[0].filerimage.image.url)
                s.plchld[p.slot] = p
    return context

@register.inclusion_tag('public/frontpage_testimonial.html', takes_context=True)
def random_testimonial(context):
    context['root'] = get_page_from_path('references')
    if context['root'] and context['root'].children.filter(published=True):
        context['testimonial'] = context['root'].children.filter(published=True).order_by('?')[0]
        for p in context['testimonial'].placeholders.all():
            context[p.slot] = p
    return context
