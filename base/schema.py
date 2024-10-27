import graphene 
from graphene_django import DjangoObjectType
from .models import User, Contract


##TESTAR TODAS AS MUTATIONS E QUERIES!!!!!!!!!!!!!!!!

#Types

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields =  ('id', 'name', 'email', 'created_at')
        
class ContractType(DjangoObjectType):
    class Meta:
        model = Contract
        fields = ('id', 'description', 'user', 'fidelity', 'amount', 'created_at',)
      
# Queries  

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    contracts = graphene.List(ContractType)
    get_user = graphene.Field(UserType, id=graphene.ID(required=True))
    get_contract = graphene.Field(ContractType, id=graphene.ID(required=True))
    get_contract_without_nested_user = graphene.Field(ContractType, id=graphene.ID(required=True))
    getContractsByUser = graphene.List(ContractType, id=graphene.ID(required=True))
    
    # lembre de fazer try-except
    def resolve_users(self, info, **kwargs):
        return User.objects.all()
    
    # lembre de fazer try-except
    def resolve_contracts(self, info, **kwargs):
        return Contract.objects.all()
    
    def resolve_get_user(self, info, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None # definir exception dedicada?
        
    def resolve_get_contract(self, info, id):
        try:
            return Contract.objects.select_related('user').get(id=id)
        except Contract.DoesNotExist:
            return None # definir exception dedicada?
    
    def resolve_get_contract_without_nested_user(self, info, id):
        try:
            contract = Contract.objects.get(id=id)
            contract.user = None
            return contract
        except Contract.DoesNotExist:
            return None # definir exception dedicada?
    
    def resolve_getContractsByUser(self, info, user_id):
        try:
            return Contract.objects.filter(user_id=user_id)
        except User.DoesNotExist:
            return [] # definir exception dedicada?
        
# Mutations

class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
    
    user = graphene.Field(UserType)
    
    def mutate(self, info, name, email):
        try:
            user = User(name=name, email=email)
            user.save()
            return CreateUser(user=user)
        
        except Exception:
            return CreateUser(user=None, message=Exception)
        
class CreateContract(graphene.Mutation):
    class Arguments:
        description = graphene.String(required=True)
        user_id = graphene.ID(required=True)
        fidelity = graphene.Int(required=True)
        amount = graphene.Float(required=True)
        
    contract = graphene.Field(ContractType)
    
    def mutate(self, info, description, user_id, fidelity, amount):
        try:
            user = User.objects.get(id=user_id)
            contract = Contract(description=description, user=user, fidelity=fidelity, amount=amount)
            contract.save()
            return CreateContract(contract=contract, message="Contract created with success.")
        
        except User.DoesNotExist:
            return CreateContract(contract=None, message="User don't exist.")
        
        except Exception:
            return CreateContract(contract=None, message=Exception)
    
class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        email = graphene.String()
        
    user = graphene.Field(UserType)
    
    def mutate(self, info, id, name=None, email=None):
        try:
            user = User.objects.get(id=id)
            
            if name:
                user.name = name
            if email:
                user.email = email
                
            user.save()
            return UpdateUser(user=user)
        
        except User.DoesNotExist:
            return UpdateUser(user=None, message="User don't exist.")
               
        except Exception:
            return UpdateUser(user=None, message=Exception)

class UpdateContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        description = graphene.String()
        fidelity = graphene.Int()
        amount = graphene.Float()
        
    contract = graphene.Field(ContractType)
    
    def mutate(self, info, id, description=None, fidelity=None, amount=None):
        try:
            contract = Contract.objects.get(id=id)
            
            if description:
                contract.description = description
            if fidelity is not None:
                contract.fidelity = fidelity
            if amount is not None:
                contract.amount = amount
                
            contract.save()
            return UpdateContract(contract=contract, message="Contract updated successfully")
        
        except Contract.DoesNotExist:
            return UpdateContract(contract=None, message="Contract don't exist.")
        
        except Exception:
            return UpdateContract(contract=None, message={str(Exception)})
        
class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success_deletion = graphene.Boolean()
        
    def mutate(self, info, id):
        try:
            User.objects.get(id=id).delete()
            return DeleteUser(success_deletion=True, message="User deleted successfully.")
        
        except User.DoesNotExist:
            return DeleteUser(success_deletion=False, message="User don't exist.")
        
        except Exception:
            return DeleteUser(success_deletion=False, message=str(Exception))

class DeleteContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success_deletion = graphene.Boolean()
    
    def mutate(self, info, id):
        try:
            Contract.objects.get(id=id).delete()
            return DeleteContract(success_deletion=True, message="Contract deleted successfully.")
        
        except Contract.DoesNotExist:
            return DeleteContract(success_deletion=False, message="Contract don't exist.")
        
        except Exception:
            return DeleteContract(success_deletion=False, message=str(Exception))
        
        
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_contract = CreateContract.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    delete_contract = DeleteContract.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)