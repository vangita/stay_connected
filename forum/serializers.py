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
    tags = TagSerializer(many=True)
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


class AnswerSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    class Meta:
        model = Answer
        fields = '__all__'

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
    class Meta:
        model = Vote
        fields = ['id', 'user', 'answer', 'vote']

    def validate(self, data):
        if data['answer'].user == data['user']:
            raise serializers.ValidationError("You cannot vote on your own answer.")
        return data
