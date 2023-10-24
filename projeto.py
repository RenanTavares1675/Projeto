from fastapi import FastAPI, HTTPException, Response
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


app = FastAPI()


class Cliente(BaseModel):
    id: int             
    nome: str           
    atendimento: str    
    posicao: int        
    dataC: datetime     
    atendido: bool      


db_cliente = [
    Cliente(id=1, nome="Renan", atendimento="N", posicao=1, dataC=datetime(2023, 10, 15), atendido=False),
    Cliente(id=2, nome="Ana", atendimento="P", posicao=2, dataC=datetime(2023, 10, 15), atendido=False),
    Cliente(id=3, nome="Gerson", atendimento="N", posicao=3, dataC=datetime(2023, 10, 15), atendido=False)
]

# Raiz
@app.get("/")
async def root():
    return {"message": "Fila do Banco"}

#ordem da fila de clientes
@app.get("/fila", response_model=List[Cliente])
async def mostrar_minha_fila(response: Response):
    if not db_cliente:
        response.status_code = 200  
        return []
    return db_cliente

# buscar cliente específico
@app.get("/fila/{id}", response_model=Cliente)
async def mostrar_fila(id: int):
    
    cliente = next((c for c in db_cliente if c.id == id), None)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

# adicionar cliente
@app.post("/fila", status_code=201)
async def criar_cliente(cliente: Cliente):
    
    maior_id = max(c.id for c in db_cliente) if db_cliente else 0
    cliente.id = maior_id + 1
  
    maior_posicao = max(c.posicao for c in db_cliente) if db_cliente else 0

    cliente.posicao = maior_posicao + 1
  
    if len(cliente.nome) > 20:
        raise HTTPException(status_code=400, detail="Nome deve ter no máximo 20 caracteres")
    if cliente.atendimento not in ["N", "P"]:
        raise HTTPException(status_code=400, detail="Tipo de atendimento deve ser 'N' ou 'P")

    cliente.dataC = datetime.now()
    cliente.atendido = False
    db_cliente.append(cliente)
    return {"mensagem": "Cliente criado com sucesso"}

#Atualizar fila
@app.put("/fila")
async def atualizar_fila():
    for cliente in db_cliente:
        cliente.posicao -= 1
        if cliente.posicao <= 0:
            cliente.atendido = True
    return {"mensagem": "Fila atualizada"}

#Excluir Fila
@app.delete("/fila/{id}")
async def deletar_cliente(id: int):
    
    cliente = next((c for c in db_cliente if c.id == id), None)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    db_cliente.remove(cliente)

    for cliente in db_cliente:
        if cliente.posicao > id:
            cliente.posicao = cliente.posicao - 1
    return {"mensagem": "Cliente removido com sucesso"}