from rest_framework import serializers
from django.contrib.auth.models import User
from tasks.models import Task, Category, Tag, Team, TeamMembership, TaskAttachment, TaskComment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'role', 'joined_at']

class TeamSerializer(serializers.ModelSerializer):
    members = TeamMembershipSerializer(source='teammembership_set', many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'created_by', 'members', 'member_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.count()

class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_size_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'uploaded_by', 'uploaded_at', 'file_size', 'file_size_formatted']
        read_only_fields = ['id', 'uploaded_at', 'file_size']

class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    team = TeamSerializer(read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    has_reminder = serializers.ReadOnlyField()
    
    # Write-only fields for IDs
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 'due_date', 'reminder_date',
            'created_at', 'updated_at', 'user', 'assigned_to', 'category', 'tags', 'team',
            'estimated_hours', 'actual_hours', 'attachments', 'comments', 'is_overdue',
            'has_reminder', 'category_id', 'assigned_to_id', 'team_id', 'tag_ids'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        task = super().create(validated_data)
        
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids, user=self.context['request'].user)
            task.tags.set(tags)
        
        return task
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        task = super().update(instance, validated_data)
        
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids, user=self.context['request'].user)
            task.tags.set(tags)
        
        return task