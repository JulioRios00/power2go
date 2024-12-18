import graphene 
from graphene_django import DjangoObjectType

from .exceptions import UserAlreadyExistsError, UserHasContractsError
from .models import User, Contract


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields =  ('id', 'name', 'email', 'created_at')
        
class ContractType(DjangoObjectType):
    user_id = graphene.ID()
    class Meta:
        model = Contract
        fields = ('id', 'description', 'user', 'fidelity', 'amount', 'created_at',)
        
    
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
    
class DeleteContractInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
      

class Query(graphene.ObjectType):
    users_gql = graphene.List(UserType)
    contracts_gql = graphene.List(ContractType)
    get_user_gql = graphene.Field(UserType, id=graphene.ID(required=True))
    get_contract_gql = graphene.Field(ContractType, input=GetContractInput(required=True))
    get_contract_without_nested_user_gql = graphene.Field(
				ContractType, 
				input=GetContractWithoutNestedUserInput(required=True)
    )
    getContractsByUser = graphene.List(
				ContractType, 
				user_id=graphene.ID(required=True)
    )
    
    def resolve_users_gql(self, info, **kwargs):
        return User.objects.all()
    
    def resolve_contracts_gql(self, info, **kwargs):
        return Contract.objects.all()
    
    def resolve_get_user_gql(self, info, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None 
        
    def resolve_get_contract_gql(self, info, input):
        try:
            return Contract.objects.select_related('user').get(id=input.id)
        except Contract.DoesNotExist:
            return None 
    
    def resolve_get_contract_without_nested_user_gql(self, info, input):
        try:
            contract = Contract.objects.get(id=input.id)
            contract.user_id
            return contract
        except Contract.DoesNotExist:
            return None 
    
    def resolve_get_contracts_by_user_gql(self, info, user_id):
        try:
            return Contract.objects.filter(user_id=user_id)
        except User.DoesNotExist:
            return [] 
        
        
class CreateUser(graphene.Mutation):
    class Arguments:
        input = CreateUserInput(required=True)
        
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    message = graphene.String()
    
    def mutate(self, info, input):
        try:    
            if User.objects.filter(email=input.email).exists():								
                raise UserAlreadyExistsError("User with this email already exists.") 
                         
            user = User(name=input.name, email=input.email)
            user.save()
            return CreateUser(
                id=user.id,
                name=user.name,
                email=user.email,
                message="User created successfully"
            )
        
        except UserAlreadyExistsError as e:
            return CreateUser(message=str(e))
        
        except Exception as e:
            return CreateUser(message=str(e))

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

 
class DeleteUser(graphene.Mutation):
    class Arguments:
        input = DeleteUserInput(required=True)
        
    success_deletion = graphene.Boolean()
    message = graphene.String()
        
    def mutate(self, info, input):
        try:
            user = User.objects.get(id=input.id)
   
            if Contract.objects.filter(user_id=user.id).exists():
                raise UserHasContractsError("User has contract(s) and cannot be deleted.")
			
            user.delete()
            return DeleteUser(success_deletion=True, message="User deleted successfully.")
			
        except User.DoesNotExist:
            return DeleteUser(success_deletion=False, message="User doesn't exist.")
			
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
        input = DeleteContractInput(required=True)
        
    success_deletion = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            Contract.objects.get(id=input.id).delete()
            return DeleteContract(success_deletion=True, message="Contract deleted successfully.")
        
        except Contract.DoesNotExist:
            return DeleteContract(success_deletion=False, message="Contract don't exist.")
        
        except Exception as e:
            return DeleteContract(success_deletion=False, message=str(e))
        
        
class Mutation(graphene.ObjectType):
    create_user_gql = CreateUser.Field()
    create_contract_gql = CreateContract.Field()
    update_user_gql = UpdateUser.Field()
    delete_user_gql = DeleteUser.Field()
    delete_contract_gql = DeleteContract.Field()
    update_contract_gql = UpdateContract.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)