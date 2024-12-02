from rest_framework import serializers

from forum.models import Tag, Question, User, Answer, Vote


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'profile_picture', 'rating']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(),many=True,slug_field='name')

    answer_count = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    has_accepted_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['user','id', 'subject', 'description', 'tags','created_at']
        fields += ['answer_count', 'has_accepted_answer']

    def get_answer_count(self, obj):
        return obj.answers.count()

    def get_has_accepted_answer(self, obj):
        return obj.answers.filter(is_accepted=True).exists()

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        question.tags.set(tags)
        return question

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance.subject = validated_data.get('subject', instance.subject)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        instance.tags.set(tags)
        return instance


class AnswerSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'content', 'user', 'question', 'created_at','is_accepted', 'votes']

    def get_votes(self, obj):
        upvotes = obj.votes.filter(vote='up').count()
        downvotes = obj.votes.filter(vote='down').count()
        return {'upvotes': upvotes, 'downvotes': downvotes}

    def validate(self, data):
        if self.instance and data.get('is_accepted') and self.instance.question.author != self.context['request'].user:
            raise serializers.ValidationError("Only the question's author can accept an answer.")
        return data


class DetailQuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    user = UserSerializer(read_only=True)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['user','id', 'subject', 'description', 'tags', 'answers','created_at']

    def get_answer(self, obj):
        return obj.answers.all()

class VoteSerializer(serializers.ModelSerializer):
    answer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Vote
        fields = ['id', 'answer_id', 'vote']

    def validate(self, data):
        if data['answer'].user == self.context['request'].user:
            raise serializers.ValidationError("You cannot vote on your own answer.")
        return data
