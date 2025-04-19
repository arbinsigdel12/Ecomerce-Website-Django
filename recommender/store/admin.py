from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Purchase, Feedback

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'feedback_count')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    
    def feedback_count(self, obj):
        return obj.feedback_set.count()
    feedback_count.short_description = 'Feedback Count'

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'purchase_date', 'total_price')
    list_filter = ('purchase_date', 'user')
    search_fields = ('product__name', 'user__username')
    list_select_related = ('user', 'product')
    
    def total_price(self, obj):
        return f"${obj.product.price * obj.quantity:.2f}"
    total_price.short_description = 'Total Price'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
     # Add raw_id_fields for faster loading with many users/products
    raw_id_fields = ('user', 'product')
    list_display = ('product', 'user', 'rating_stars', 'comment', 'created_at')

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return f"{stars} ({obj.get_rating_display()})"
    rating_stars.short_description = "Rating"    
    # Show more fields in list view
    list_display = ('id', 'product', 'user', 'rating_stars', 'created_at', 'is_reviewed')
    
    # Add this to see ALL feedback (including empty comments)
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')
    list_display = ('product_link', 'user_link', 'rating_stars', 'comment_preview', 
                   'created_at', 'is_reviewed')
    list_filter = ('rating', 'is_reviewed', 'created_at', 'product')
    search_fields = ('product__name', 'user__username', 'comment')
    list_editable = ('is_reviewed',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    actions = ['mark_as_reviewed', 'mark_as_unreviewed']
    
  
    def comment_preview(self, obj):
        return format_html(
            '<div title="{}" style="max-width:300px;overflow:hidden;text-overflow:ellipsis">{}</div>',
            obj.comment,
            obj.comment
        )
    comment_preview.short_description = 'Comment'
    
    def product_link(self, obj):
        url = reverse('admin:store_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def rating_display(self, obj):
        colors = {1: 'red', 2: 'orange', 3: 'blue', 4: 'green', 5: 'gold'}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.rating, 'black'),
            obj.get_rating_display()
        )
    rating_display.short_description = 'Rating'
    
    def comment_short(self, obj):
        return obj.comment[:50] + '...' if obj.comment else ''
    comment_short.short_description = 'Comment'
    
    # Action methods
    def mark_as_reviewed(self, request, queryset):
        queryset.update(is_reviewed=True)
    mark_as_reviewed.short_description = "Mark selected as reviewed"
    
    def mark_as_unreviewed(self, request, queryset):
        queryset.update(is_reviewed=False)
    mark_as_unreviewed.short_description = "Mark selected as unreviewed"