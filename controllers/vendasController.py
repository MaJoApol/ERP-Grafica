from flask import request
from database.db import db
from models.vendas import Vendas
from models.vendas_produtos import Vendas_produtos
from models.produtos import Produtos
def vendasController():

    if request.method == 'POST':
        try:
            data = request.get_json() # converte em python
            
            vendas = Vendas(data['idCliente'], data['idVendedor'], data['data'], data['isVendaOS'], data['situacao'], data['desconto'])
            
            dataProdutos = data.get('vendas_produtos', [])

            db.session.add(vendas)
            db.session.flush() # para conseguir pegar id
            
            for dataP in dataProdutos:
                idP = dataP['idProduto']
                quantidade = dataP['quantidade']
                vendas_produtos = Vendas_produtos(vendas.id, idP, quantidade)
                db.session.add(vendas_produtos)
            
            db.session.commit()
            return 'Vendas adicionados com sucesso!', 200
        except Exception as e:
            return f'Não foi possível inserir. Erro {str(e)}', 405
        

    elif request.method == 'GET':
        try:
            dataVendas = Vendas.query.all()
            dataVendas_produtos = Vendas_produtos.query.all()
            newDataVendas = {'vendas': [venda.to_dict() for venda in dataVendas]}
            newDataVendas_produtos = {'vendas_produtos': [venda_produto.to_dict() for venda_produto in dataVendas_produtos]} #pegando cada obj venda, e tranformando num dicionario


            idVenda = []
            fkVenda = []

            for produto in newDataVendas_produtos['vendas_produtos']:
                fkVenda.append(produto['idVenda']) 

            for venda in newDataVendas['vendas']:
                idVenda.append(venda['id'])

                for item in idVenda:
                    for fk in fkVenda:
                        if fk == item:
                            getVendas = {'vendas':[[venda.to_dict() for venda in dataVendas],[produto.to_dict() for produto in dataVendas_produtos]]}
                        else:
                            getVendas = {'vendas':[venda.to_dict() for venda in dataVendas]}

            
            return getVendas, 200
        
        except Exception as e:
            return f'Não foi possível buscar. Erro {str(e)}', 405
        

    elif request.method == 'PUT':
            try:
                id = request.args.to_dict().get('id')
                venda = Vendas.query.get(id)
                data = request.get_json() #pega todos os dados 
                dataVendas_produtos = data.get('vendas_produtos', []) #preciso pegar os ID's disso aqui, passa no json           

                for produto in dataVendas_produtos:
                    id_vp = produto.get('id')
                    #print("produto", produto)
                    vendas_produtos = Vendas_produtos.query.filter(Vendas_produtos.idVenda == id).all()
                    #print(vendas_produtos)
                    #print(len(vendas_produtos))
                        
                    for produto_vp in vendas_produtos:
                        
                        #print(id_vp)
                        #print(produto_vp.id)
                        if produto_vp.id == id_vp:
                            #print("OOOOLOKO")
                            produto_vp.idProduto = produto.get('idProduto')
                            produto_vp.quantidade = produto.get('quantidade')                       
                            db.session.commit()  
                

                if venda is None:
                    return{'error': 'venda não encontrado'}, 405
                
                venda.idCliente = data.get('idCliente', venda.idCliente)
                venda.idVendedor = data.get('idVendedor', venda.idVendedor)   
                venda.data = data.get('data', venda.data)   
                venda.isVendaOS = data.get('isVendaOS', venda.isVendaOS)   
                venda.situacao = data.get('situacao', venda.situacao)
                venda.desconto = data.get('desconto', venda.desconto)
     
                db.session.commit()

                return "venda atualizado com sucesso", 202

            except Exception as e:
                return f"Não foi possível atualizar a venda. Erro:{str(e)}", 405
            

    elif request.method == 'DELETE':
        try:
            id = request.args.to_dict().get('id') #pega o id dos dados que o data trouxe do front
            venda = Vendas.query.get(id) # vai procurar vendas NO BANCO com esse id

            dataVendas_produtos = Vendas_produtos.query.all()
            newDataVendas_produtos = {'vendas_produtos': [venda_produto.to_dict() for venda_produto in dataVendas_produtos]} #pegando cada obj venda, e tranformando num dicionario
            
            for produto in newDataVendas_produtos['vendas_produtos']:
                if int(produto['idVenda']) == int(id):
                    vendas_produtos = Vendas_produtos.query.get(produto['id'])
                    db.session.delete(vendas_produtos)

            if venda is None:
                return{'error': 'venda não encontrado'}, 405
            
            db.session.delete(venda)
            db.session.commit()
            return "venda deletado com sucesso", 202

        except Exception as e:
            return f"Não foi possível apagar o venda. Erro:{str(e)}", 405
        

