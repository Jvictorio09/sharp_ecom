"""
Content Helpers
Converts database models to JSON format for templates
"""
from .models import (
    SEO, Navigation, Hero, About, Stat, Service,
    Portfolio, PortfolioProject, Testimonial, FAQ, FAQItem,
    Contact, ContactInfo, ContactFormField, SocialLink, Footer
)


def get_homepage_content_from_db():
    """
    Get all homepage content from database and convert to JSON-like dict.
    Falls back gracefully if models don't exist yet.
    """
    content = {}
    
    try:
        # SEO
        seo = SEO.objects.filter(page='home').first()
        if seo:
            content['seo'] = {
                'title': seo.title,
                'description': seo.description,
                'keywords': seo.keywords,
                'og_image_url': seo.og_image_url,
            }
    except Exception:
        pass
    
    try:
        # Navigation
        nav_items = Navigation.objects.filter(is_active=True).order_by('sort_order')
        content['navigation'] = [
            {
                'label': item.label,
                'url': item.url,
                'is_external': item.is_external,
            }
            for item in nav_items
        ]
    except Exception:
        pass
    
    try:
        # Hero
        hero = Hero.objects.filter(is_active=True).first()
        if hero:
            content['hero'] = {
                'title': hero.title,
                'subtitle': hero.subtitle,
                'cta_text': hero.cta_text,
                'cta_url': hero.cta_url,
                'background_image_url': hero.background_image_url,
            }
    except Exception:
        pass
    
    try:
        # About
        about = About.objects.filter(is_active=True).first()
        if about:
            content['about'] = {
                'title': about.title,
                'content': about.content,
                'image_url': about.image_url,
            }
    except Exception:
        pass
    
    try:
        # Stats
        stats = Stat.objects.filter(is_active=True).order_by('sort_order')
        content['stats'] = [
            {
                'label': stat.label,
                'value': stat.value,
                'icon': stat.icon,
            }
            for stat in stats
        ]
    except Exception:
        pass
    
    try:
        # Services
        services = Service.objects.filter(is_active=True).order_by('sort_order')
        content['services'] = [
            {
                'title': service.title,
                'description': service.description,
                'icon': service.icon,
                'image_url': service.image_url,
            }
            for service in services
        ]
    except Exception:
        pass
    
    try:
        # Portfolio
        portfolio = Portfolio.objects.filter(is_active=True).first()
        if portfolio:
            projects = PortfolioProject.objects.filter(
                portfolio=portfolio, is_active=True
            ).order_by('sort_order')
            content['portfolio'] = {
                'title': portfolio.title,
                'subtitle': portfolio.subtitle,
                'projects': [
                    {
                        'title': project.title,
                        'description': project.description,
                        'image_url': project.image_url,
                        'project_url': project.project_url,
                    }
                    for project in projects
                ]
            }
    except Exception:
        pass
    
    try:
        # Testimonials
        testimonials = Testimonial.objects.filter(is_active=True).order_by('sort_order')
        content['testimonials'] = [
            {
                'name': testimonial.name,
                'role': testimonial.role,
                'company': testimonial.company,
                'content': testimonial.content,
                'image_url': testimonial.image_url,
                'rating': testimonial.rating,
            }
            for testimonial in testimonials
        ]
    except Exception:
        pass
    
    try:
        # FAQs
        faq = FAQ.objects.filter(is_active=True).first()
        if faq:
            faq_items = FAQItem.objects.filter(faq=faq, is_active=True).order_by('sort_order')
            content['faq'] = {
                'title': faq.title,
                'subtitle': faq.subtitle,
                'items': [
                    {
                        'question': item.question,
                        'answer': item.answer,
                    }
                    for item in faq_items
                ]
            }
    except Exception:
        pass
    
    try:
        # Contact
        contact = Contact.objects.filter(is_active=True).first()
        if contact:
            info_items = ContactInfo.objects.filter(
                contact=contact, is_active=True
            ).order_by('sort_order')
            form_fields = ContactFormField.objects.filter(
                contact=contact, is_active=True
            ).order_by('sort_order')
            content['contact'] = {
                'title': contact.title,
                'subtitle': contact.subtitle,
                'info': [
                    {
                        'label': info.label,
                        'value': info.value,
                        'icon': info.icon,
                    }
                    for info in info_items
                ],
                'form_fields': [
                    {
                        'label': field.label,
                        'field_type': field.field_type,
                        'name': field.name,
                        'placeholder': field.placeholder,
                        'required': field.required,
                    }
                    for field in form_fields
                ]
            }
    except Exception:
        pass
    
    try:
        # Social Links
        social_links = SocialLink.objects.filter(is_active=True).order_by('sort_order')
        content['social_links'] = [
            {
                'platform': link.platform,
                'url': link.url,
                'icon': link.icon,
            }
            for link in social_links
        ]
    except Exception:
        pass
    
    try:
        # Footer
        footer = Footer.objects.first()
        if footer:
            content['footer'] = {
                'copyright_text': footer.copyright_text,
                'additional_text': footer.additional_text,
            }
    except Exception:
        pass
    
    return content

