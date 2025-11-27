"""
Management command to import homepage data from JSON
Usage: python manage.py import_homepage_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
import json
import os
from myApp.models import (
    SEO, Navigation, Hero, About, Stat, Service,
    Portfolio, PortfolioProject, Testimonial, FAQ, FAQItem,
    Contact, ContactInfo, ContactFormField, SocialLink, Footer
)


class Command(BaseCommand):
    help = 'Import homepage data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON file (optional, defaults to homepage_data.json)',
            default='homepage_data.json'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.WARNING(f'File {file_path} not found. Skipping import.')
            )
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading JSON file: {str(e)}')
            )
            return
        
        with transaction.atomic():
            # Import SEO
            if 'seo' in data:
                seo, created = SEO.objects.get_or_create(page='home')
                seo.title = data['seo'].get('title', '')
                seo.description = data['seo'].get('description', '')
                seo.keywords = data['seo'].get('keywords', '')
                seo.og_image_url = data['seo'].get('og_image_url', '')
                seo.save()
                self.stdout.write(self.style.SUCCESS('✓ SEO imported'))
            
            # Import Navigation
            if 'navigation' in data:
                Navigation.objects.all().delete()  # Clear existing
                for idx, item in enumerate(data['navigation']):
                    Navigation.objects.create(
                        label=item.get('label', ''),
                        url=item.get('url', ''),
                        sort_order=idx,
                        is_active=item.get('is_active', True),
                        is_external=item.get('is_external', False),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Navigation imported'))
            
            # Import Hero
            if 'hero' in data:
                hero, created = Hero.objects.get_or_create(id=1)
                hero.title = data['hero'].get('title', '')
                hero.subtitle = data['hero'].get('subtitle', '')
                hero.cta_text = data['hero'].get('cta_text', '')
                hero.cta_url = data['hero'].get('cta_url', '')
                hero.background_image_url = data['hero'].get('background_image_url', '')
                hero.is_active = data['hero'].get('is_active', True)
                hero.save()
                self.stdout.write(self.style.SUCCESS('✓ Hero imported'))
            
            # Import About
            if 'about' in data:
                about, created = About.objects.get_or_create(id=1)
                about.title = data['about'].get('title', '')
                about.content = data['about'].get('content', '')
                about.image_url = data['about'].get('image_url', '')
                about.is_active = data['about'].get('is_active', True)
                about.save()
                self.stdout.write(self.style.SUCCESS('✓ About imported'))
            
            # Import Stats
            if 'stats' in data:
                Stat.objects.all().delete()
                for idx, stat in enumerate(data['stats']):
                    Stat.objects.create(
                        label=stat.get('label', ''),
                        value=stat.get('value', ''),
                        icon=stat.get('icon', ''),
                        sort_order=idx,
                        is_active=stat.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Stats imported'))
            
            # Import Services
            if 'services' in data:
                Service.objects.all().delete()
                for idx, service in enumerate(data['services']):
                    Service.objects.create(
                        title=service.get('title', ''),
                        description=service.get('description', ''),
                        icon=service.get('icon', ''),
                        image_url=service.get('image_url', ''),
                        sort_order=idx,
                        is_active=service.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Services imported'))
            
            # Import Portfolio
            if 'portfolio' in data:
                portfolio, created = Portfolio.objects.get_or_create(id=1)
                portfolio.title = data['portfolio'].get('title', '')
                portfolio.subtitle = data['portfolio'].get('subtitle', '')
                portfolio.is_active = data['portfolio'].get('is_active', True)
                portfolio.save()
                
                PortfolioProject.objects.all().delete()
                for idx, project in enumerate(data['portfolio'].get('projects', [])):
                    PortfolioProject.objects.create(
                        portfolio=portfolio,
                        title=project.get('title', ''),
                        description=project.get('description', ''),
                        image_url=project.get('image_url', ''),
                        project_url=project.get('project_url', ''),
                        sort_order=idx,
                        is_active=project.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Portfolio imported'))
            
            # Import Testimonials
            if 'testimonials' in data:
                Testimonial.objects.all().delete()
                for idx, testimonial in enumerate(data['testimonials']):
                    Testimonial.objects.create(
                        name=testimonial.get('name', ''),
                        role=testimonial.get('role', ''),
                        company=testimonial.get('company', ''),
                        content=testimonial.get('content', ''),
                        image_url=testimonial.get('image_url', ''),
                        rating=testimonial.get('rating', 5),
                        sort_order=idx,
                        is_active=testimonial.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Testimonials imported'))
            
            # Import FAQs
            if 'faq' in data:
                faq, created = FAQ.objects.get_or_create(id=1)
                faq.title = data['faq'].get('title', '')
                faq.subtitle = data['faq'].get('subtitle', '')
                faq.is_active = data['faq'].get('is_active', True)
                faq.save()
                
                FAQItem.objects.all().delete()
                for idx, item in enumerate(data['faq'].get('items', [])):
                    FAQItem.objects.create(
                        faq=faq,
                        question=item.get('question', ''),
                        answer=item.get('answer', ''),
                        sort_order=idx,
                        is_active=item.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ FAQs imported'))
            
            # Import Contact
            if 'contact' in data:
                contact, created = Contact.objects.get_or_create(id=1)
                contact.title = data['contact'].get('title', '')
                contact.subtitle = data['contact'].get('subtitle', '')
                contact.is_active = data['contact'].get('is_active', True)
                contact.save()
                
                ContactInfo.objects.all().delete()
                for idx, info in enumerate(data['contact'].get('info', [])):
                    ContactInfo.objects.create(
                        contact=contact,
                        label=info.get('label', ''),
                        value=info.get('value', ''),
                        icon=info.get('icon', ''),
                        sort_order=idx,
                        is_active=info.get('is_active', True),
                    )
                
                ContactFormField.objects.all().delete()
                for idx, field in enumerate(data['contact'].get('form_fields', [])):
                    ContactFormField.objects.create(
                        contact=contact,
                        label=field.get('label', ''),
                        field_type=field.get('field_type', 'text'),
                        name=field.get('name', ''),
                        placeholder=field.get('placeholder', ''),
                        required=field.get('required', True),
                        sort_order=idx,
                        is_active=field.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Contact imported'))
            
            # Import Social Links
            if 'social_links' in data:
                SocialLink.objects.all().delete()
                for idx, link in enumerate(data['social_links']):
                    SocialLink.objects.create(
                        platform=link.get('platform', ''),
                        url=link.get('url', ''),
                        icon=link.get('icon', ''),
                        sort_order=idx,
                        is_active=link.get('is_active', True),
                    )
                self.stdout.write(self.style.SUCCESS('✓ Social Links imported'))
            
            # Import Footer
            if 'footer' in data:
                footer, created = Footer.objects.get_or_create(id=1)
                footer.copyright_text = data['footer'].get('copyright_text', '')
                footer.additional_text = data['footer'].get('additional_text', '')
                footer.save()
                self.stdout.write(self.style.SUCCESS('✓ Footer imported'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Import completed successfully!'))

