import graphene 
from graphene_django import DjangoObjectType
from .models import User, Contract

class UserType(DjangoObjectType):
    class Meta:
        model = User
        
class ContractType(DjangoObjectType):
    class Meta:
        model = Contract
        
class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    contracts = graphene.List(ContractType)
    
    def resolve_user(self, info, **kwargs):
        return User.objects.all()
    
    def resolve_contracts(self, info, **kwargs):
        return Contract.objects.all()
    
class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
    
    user = graphene.Field(UserType)
    
    def mutate(self, name, email):
        user = User(name=name, email=email)
        user.save()
        return CreateUser(user=user)
    
class CreateContract(graphene.Mutation):
    class Arguments:
        description = graphene.String(required=True)
        user_id = graphene.ID(required=True)
        fidelity = graphene.Int(required=True)
        amount = graphene.Float(required=True)
        
    contract = graphene.Field(ContractType)
    
    def mutate(self, info, description, user_id, fidelity, amount):
        user = User.objects.get(id=user_id)
        contract = Contract(description=description, user=user, fidelity=fidelity, amount=amount)
        contract.save()
        return CreateContract(contract=contract)
    
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_contract = CreateContract.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)