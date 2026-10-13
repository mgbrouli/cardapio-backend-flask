# Guia rápido

## Executar

```powershell
pip install -r requirements.txt
python run.py
```

O servidor local fica em `http://localhost:5000`; a documentação automática
da API fica em `/docs`. Veja [COMO_EXECUTAR.md](./COMO_EXECUTAR.md) para
configuração de produção.

## Endpoints

| Método | Caminho | Uso |
| --- | --- | --- |
| GET | `/` | Página inicial |
| GET | `/{empresa_id}` | Cardápio público |
| GET/POST | `/cadastro` | Criar conta |
| GET/POST | `/login` | Iniciar sessão |
| GET | `/logout` | Encerrar sessão |
| GET | `/empresa/home` | Painel autenticado |
| GET/POST | `/empresa/config/{empresa_id}` | Configurar empresa |
| POST | `/produto/add/{empresa_id}` | Criar produto |
| POST | `/produto/edit/{produto_id}` | Editar produto |
| DELETE | `/produto/delete/{produto_id}` | Excluir produto |

As URLs legadas usadas pelo frontend atual continuam disponíveis.

## Segurança de senha

As novas senhas são armazenadas com Argon2. No login, hashes antigos são
verificados e atualizados automaticamente após autenticação válida.

Para configurar ambiente, Asaas e chave de sessão, consulte
[CONFIGURACAO_ENV.md](./CONFIGURACAO_ENV.md).
