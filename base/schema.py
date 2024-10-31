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
    user_id = graphene.ID()
    class Meta:
        model = Contract
        fields = ('id', 'description', 'user', 'fidelity', 'amount', 'created_at',)
        
# Inputs
class GetUserInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    
class CreateUserInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)

class UpdateUserInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    email = graphene.String()
    
class DeleteUserInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
         
class CreateContractInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    user_id = graphene.ID(required=True)
    fidelity = graphene.Int(required=True)
    amount = graphene.Float(required=True)
    
class GetContractInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    
class GetContractWithoutNestedUserInput(graphene.InputObjectType): 
    id = graphene.ID(required=True)

class UpdateContractInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    description = graphene.String()
    fidelity = graphene.Int()
    amount = graphene.Float()
      
# Queries  

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    contracts = graphene.List(ContractType)
    get_user = graphene.Field(UserType, input=GetUserInput(required=True))
    get_contract = graphene.Field(ContractType, input=GetContractInput(required=True))
    get_contract_without_nested_user = graphene.Field(
				ContractType, 
				input=GetContractWithoutNestedUserInput(required=True)
    )
    getContractsByUser = graphene.List(
				ContractType, 
				user_id=graphene.ID(required=True)
    )
    
    # lembre de fazer try-except
    def resolve_users(self, info, **kwargs):
        return User.objects.all()
    
    # lembre de fazer try-except
    def resolve_contracts(self, info, **kwargs):
        return Contract.objects.all()
    
    def resolve_get_user(self, info, input):
        try:
            return User.objects.get(id=input.id)
        except User.DoesNotExist:
            return None # definir exception dedicada?
        
    def resolve_get_contract(self, info, input):
        try:
            return Contract.objects.select_related('user').get(id=input.id)
        except Contract.DoesNotExist:
            return None # definir exception dedicada?
    
    def resolve_get_contract_without_nested_user(self, info, input):
        try:
            contract = Contract.objects.get(id=input.id)
            contract.user_id
            return contract
        except Contract.DoesNotExist:
            return None # definir exception dedicada?
    
    def resolve_get_contracts_by_user(self, info, user_id):
        try:
            return Contract.objects.filter(user_id=user_id)
        except User.DoesNotExist:
            return [] # definir exception dedicada?
        
        
class CreateUser(graphene.Mutation):
    class Arguments:
        input = CreateUserInput(required=True)
        
    user = graphene.Field(UserType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            user = User(name=input.name, email=input.email)
            user.save()
            return CreateUser(user=user)
        
        except Exception:
            return CreateUser(user=None, message=Exception)

class UpdateUser(graphene.Mutation):
    class Arguments:
        input = UpdateUserInput(required=True)
        
    user = graphene.Field(UserType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            user = User.objects.get(id=input.id)
            
            if input.name:
                user.name = input.name
            if input.email:
                user.email = input.email
                
            user.save()
            return UpdateUser(user=user)
        
        except User.DoesNotExist:
            return UpdateUser(user=None, message="User don't exist.")
               
        except Exception as e:
            return UpdateUser(user=None, message=str(e))

# Tratar info caso id não seja encontrado  
class DeleteUser(graphene.Mutation):
    class Arguments:
        input = DeleteUserInput(required=True)
        
    success_deletion = graphene.Boolean()
    message = graphene.String()
        
    def mutate(self, info, input):
        try:
            User.objects.get(id=input.id).delete()
            return DeleteUser(success_deletion=True, message="User deleted successfully.")
        
        except User.DoesNotExist:
            return DeleteUser(success_deletion=False, message="User don't exist.")
        
        except Exception as e:
            return DeleteUser(success_deletion=False, message=str(e))
      
class CreateContract(graphene.Mutation):
    class Arguments:
        input = CreateContractInput(required=True)
        
    contract = graphene.Field(ContractType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            user = User.objects.get(id=input.user_id)
            contract = Contract(
                description=input.description, 
                user=user, 
                fidelity=input.fidelity, 
                amount=input.amount
            )
            contract.save()
            return CreateContract(contract=contract, message="Contract created successfully.")
        
        except User.DoesNotExist:
            return CreateContract(contract=None, message="User don't exist.")
        
        except Exception as e:
            return CreateContract(contract=None, message=str(e))
    
class UpdateContract(graphene.Mutation):
    class Arguments:
        input = UpdateContractInput(required=True)
        
    contract = graphene.Field(ContractType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            contract = Contract.objects.get(id=input.id)
            
            if input.description:
                contract.description = input.description
            if input.fidelity is not None:
                contract.fidelity = input.fidelity
            if input.amount is not None:
                contract.amount = input.amount
                
            contract.save()
            return UpdateContract(contract=contract, message="Contract updated successfully")
        
        except Contract.DoesNotExist:
            return UpdateContract(contract=None, message="Contract don't exist.")
        
        except Exception as e:
            return UpdateContract(contract=None, message=str(e))

class DeleteContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success_deletion = graphene.Boolean()
    message = graphene.String()
    
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
    update_contract = UpdateContract.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)