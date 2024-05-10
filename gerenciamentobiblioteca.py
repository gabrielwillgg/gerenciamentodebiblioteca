import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import pyodbc

#dados necessários para podermos criar e nos conectar com o banco de dados
dados_conexao = ("Driver={SQLite3 ODBC Driver};"
                 "Server=localhost;"
                 "Database=EstoqueBiblioteca.sqlite3") 
conexao = pyodbc.connect(dados_conexao) #conectando com o banco de dados
cursor = conexao.cursor() #cursor necessário para podermos fazer todas as manipulações


def cadastrar_livros(titulo_livro, nome_autor, ano_publicacao, qtd_livros, id_livros):
    titulo = titulo_livro.get() # pegar o valor digitado na caixa de texto título
    autor = nome_autor.get() # pegar o valor digitado na caixa de texto autor
    ano = ano_publicacao.get() # pegar o valor digitado na caixa de texto ano
    quantidade = qtd_livros.get() # pegar o valor digitado na caixa de texto quantidade
    id = id_livros.get() # pegar o valor digitado na caixa de texto id

    try: # tratamento de erro para caso não preencha alguma caixa apareça um aviso.
        # se existir o id informado na caixa de texto dentro do banco de dados, ele atualiza a quantidade de livros
        if cursor.execute(f"SELECT * FROM Livros WHERE id = '{id}'").fetchone() is not None: 
            comando = f"""UPDATE Livros
            SET quantidade = quantidade + {quantidade}
            WHERE id = '{id}';
            """
            cursor.execute(comando) # executando o comando
            cursor.commit() # efetuando o commit para poder atualizar no banco de dados.

            # pop-up informando que o comando foi executado com sucesso
            tkinter.messagebox.showinfo(title="Livro adicionado",message="Livro já existente, quantidade atualizada com sucesso")

        else: # caso não existir o id informado dentro do banco de dados, ele vai inserir o livro
            comando = f"""INSERT INTO Livros(id, titulo, autor, ano, quantidade)
            VALUES
            ('{id}', '{titulo}', '{autor}', '{ano}', '{quantidade}')
            """
            cursor.execute(comando) # executando o comando
            cursor.commit() # efetuando o commit para poder atualizar no banco de dados.

            # pop-up informando que o comando foi executado com sucesso
            tkinter.messagebox.showinfo(title="Livro adicionado",message="Livro adicionado com sucesso")

    except: # caso der algum erro, aparece um pop-up de aviso
        tkinter.messagebox.showerror("Erro","Certifique-se se inseriu os dados corretamente. Os campos id, ano e quantidade são apenas para números.")


def cadastrar_usuarios(nome, id, telefone, email):
    nome = nome.get() # pegar o valor digitado na caixa de texto nome_usuario
    id = id.get() # pegar o valor digitado na caixa de texto numero_identificacao
    telefone = telefone.get() # pegar o valor digitado na caixa de texto numero_telefone
    email = email.get() # pegar o valor digitado na caixa de texto email

    try: # tratamento de erro para caso não preencha alguma caixa apareça um aviso.
        # caso o id do usuário já exista no banco de dados, mostra um aviso de usuário existente.
        if cursor.execute(f"SELECT * FROM Usuarios WHERE id = '{id}'").fetchone() is not None:
            tkinter.messagebox.showinfo(title="Usuário já existente",message=f"O usuário com id {id} já existe.")
        else: # caso não exista, ele insere um novo usuário
            comando = f"""INSERT INTO Usuarios(id, nome, telefone, email)
            VALUES
            ('{id}', '{nome}', '{telefone}', '{email}')
            """
            cursor.execute(comando) # executando o comando
            cursor.commit() # efetuando o commit para poder atualizar no banco de dados.

            # pop-up informando que o comando foi executado com sucesso
            tkinter.messagebox.showinfo(title="Usuário adicionado",message="Usuário adicionado com sucesso.")

    except:# caso der algum erro, aparece um pop-up de aviso
        tkinter.messagebox.showerror("Erro","Certifique-se se inseriu os dados corretamente. Os campos id e telefone são apenas para números.")

def emprestimo_livros(id_usuario, id_livro):
    id_usuario = id_usuario.get() # pegar o valor digitado na caixa de texto id_usuario
    id_livro = id_livro.get() # pegar o valor digitado na caixa de texto id_livro

    usuarios = cursor.execute(f"SELECT * FROM Usuarios WHERE id = '{id_usuario}'").fetchone() # extrair, caso exista, o usuário com o mesmo id
    livros = cursor.execute(f"SELECT * FROM Livros WHERE id = '{id_livro}'").fetchone() # extrair, caso exista, o livro com o mesmo id

    # identificar se já existe empréstimo com o mesmo usuário e mesmo livro, para limitar apenas 1 empréstimo por livro e pessoa
    emprestimo = cursor.execute(f"SELECT 1 FROM Emprestimos WHERE id_usuario = '{id_usuario}' AND id_livro = '{id_livro}'").fetchone()

    if usuarios is not None and livros is not None and emprestimo is None: # caso o id do usuário e livro esteja preenchido e não exista um empréstimo
        if livros[4] > 0: # verificação para saber a disponibilidade do livro
            # inserindo na tabela de empréstimos
            comando = f"""INSERT INTO Emprestimos(id_usuario, id_livro)
            VALUES
            ('{id_usuario}', '{id_livro}');
            """
            cursor.execute(comando)
            cursor.commit()
            # removendo uma unidade do livro escolhido
            comando = f"""UPDATE Livros
            SET quantidade = quantidade - 1
            WHERE id = '{id_livro}';
            """
            cursor.execute(comando)
            cursor.commit()
            # pop-up informando que o comando foi executado com sucesso
            tkinter.messagebox.showinfo(title="Empréstimo adicionado",message="Empréstimo adicionado com sucesso.")
        else: # caso a quantidade do livro escolhido seja 0, aparece um pop-up avisando.
            tkinter.messagebox.showinfo(title="Livro em falta",message=f"O livro de id {id_livro} está em falta.")
    elif emprestimo is not None: # caso já tenha um empréstimo realizado com o mesmo id de usuário e livro
        tkinter.messagebox.showinfo(title="Emprestimo já realizado",message=f"Empréstimo já realizado, limite de um livro por usuário. Favor escolher outro livro.")
    elif usuarios is None: # caso não tenha nenhum usuário com o id informado no banco de dados
        tkinter.messagebox.showinfo(title="Usuário não identificado",message=f"Usuário de id {id_usuario} não identificado no banco de dados.")
    else: # caso não tenha nenhum livro com o id informado no banco de dados
        tkinter.messagebox.showinfo(title="Livro não identificado",message=f"Livro de id {id_livro} não identificado no banco de dados.")


def devolucao_livros(id_usuario, id_livro):
    id_usuario = id_usuario.get() # pegar o valor digitado na caixa de texto id_usuario
    id_livro = id_livro.get() # pegar o valor digitado na caixa de texto id_livro

    # selecionar, caso exista, o empréstimo com o mesmo usuário e mesmo livro
    verificacao = cursor.execute(f"SELECT * FROM Emprestimos WHERE id_usuario = '{id_usuario}' AND id_livro = '{id_livro}'").fetchone()

    if verificacao is not None: # caso exista o empréstimo, deleta o empréstimo da tabela de empréstimos e adiciona 1 na quantidade do livro
        # deletando o empréstimo na tabela de empréstimos
        comando = f"""DELETE FROM Emprestimos
        WHERE id_usuario = '{id_usuario}' AND id_livro = '{id_livro}';
        """
        cursor.execute(comando)
        cursor.commit()
        # adicionando uma unidade do livro escolhido
        comando = f"""UPDATE Livros
        SET quantidade = quantidade + 1
        WHERE id = '{id_livro}';
        """
        cursor.execute(comando)
        cursor.commit()
        # pop-up informando que o comando foi executado com sucesso
        tkinter.messagebox.showinfo(title="Devolução realizada",message="Devolução realizada com sucesso.")
    else: # caso não tenha nenhum empréstimo com os ids informados no banco de dados
        tkinter.messagebox.showinfo(title="Não existe empréstimo",message=f"Não existe empréstimo com os parâmetros passados.")


def consultar_livros(titulo, autor, ano, id):
    titulo = titulo.get() # pegar o valor digitado na caixa de texto titulo
    autor = autor.get() # pegar o valor digitado na caixa de texto autor
    ano = ano.get() # pegar o valor digitado na caixa de texto ano
    id = id.get() # pegar o valor digitado na caixa de texto id

    # comando para filtrar as inserções na caixa de texto
    # caso tenha alguma parâmetro vazio na caixa de texto
    # ele retornará todas as linhas para poder satisfazer as condições
    comando = f"""SELECT * FROM Livros
    WHERE titulo = IFNULL(NULLIF('{titulo}', ''), titulo)
    AND autor = IFNULL(NULLIF('{autor}', ''), autor)
    AND ano = IFNULL(NULLIF('{ano}', ''), ano)
    AND id = IFNULL(NULLIF('{id}', ''), id)
    """
    resultado = cursor.execute(comando).fetchall()
    
    if resultado: # caso exista algum resultado da busca
        # formatando o texto para exibir os livros encontrados
        mensagem = 'ID | Título | Autor | Ano | Quantidade\n'
        for linha in resultado:
            for coluna in linha:
                mensagem += str(coluna) + ' | '
            mensagem += '\n'
        # pop-up informando que o comando foi executado com sucesso
        tkinter.messagebox.showinfo(title="Estoque de Livros",message=f"{mensagem}")
    else: # caso não exista algum resultado, mostra um pop-up com aviso.
        tkinter.messagebox.showinfo(title="Estoque de Livros",message="Nenhum livro foi encontrado no estoque.")

def livros_disponiveis():
    # seleciona todos os livros que a quantidade é maior que 0 e armazena na variável resultado
    resultado = cursor.execute(f"""SELECT * FROM Livros WHERE quantidade > 0""").fetchall()
    if resultado: # caso exista algum livro com quantidade maior que 0
        # formatando o texto para exibir os livros encontrados
        mensagem = 'ID | Título | Autor | Ano | Quantidade\n'
        for linha in resultado:
            for coluna in linha:
                mensagem += str(coluna) + ' | '
            mensagem += '\n'
        # pop-up informando que o comando foi executado com sucesso
        tkinter.messagebox.showinfo(title="Livros Disponíveis",message=f"{mensagem}")
    else: # caso não exista algum resultado, mostra um pop-up com aviso
        tkinter.messagebox.showinfo(title="Livros Disponíveis",message="Não existe nenhum livro disponível no momento.")

def livros_emprestados():
    # seleciona todos os empréstimos e seleciona o título do livro da tabela Livros e o Nome e Email do usuário na tabela Usuários
    comando = """SELECT Emprestimos.*, Livros.titulo, Usuarios.nome, Usuarios.email FROM Emprestimos
    INNER JOIN Usuarios ON Emprestimos.id_usuario = Usuarios.id
    INNER JOIN Livros ON Emprestimos.id_livro = Livros.id
    """
    # armazena o retorno na variável resultado
    resultado = cursor.execute(comando).fetchall()

    if resultado: # caso exista algum empréstimo registrado
        # formatando o texto para exibir os livros encontrados
        mensagem = 'ID Usuário | ID Livro | Título | Nome do Usuário | Email |\n'
        for linha in resultado:
            for coluna in linha:
                mensagem += str(coluna) + ' | '
            mensagem += '\n'
        # pop-up informando que o comando foi executado com sucesso
        tkinter.messagebox.showinfo(title="Livros Emprestados",message=f"{mensagem}")
    else: # caso não exista algum resultado, mostra um pop-up com aviso
        tkinter.messagebox.showinfo(title="Livros Emprestados",message="Não existe nenhum livro emprestado.")


def usuarios_cadastrados():
    # seleciona todos os usuários, caso tenha, da tabela Usuários e armazena na variável resultado.
    resultado = cursor.execute(f"""SELECT * FROM Usuários""").fetchall()
    if resultado: # caso exista algum usuário cadastrado
        # formatando o texto para exibir os livros encontrados
        mensagem = 'ID | Nome | Telefone | Email |\n'
        for linha in resultado:
            for coluna in linha:
                mensagem += str(coluna) + ' | '
            mensagem += '\n'
        # pop-up informando que o comando foi executado com sucesso
        tkinter.messagebox.showinfo(title="Usuários cadastrados",message=f"{mensagem}")
    else: # caso não exista algum resultado, mostra um pop-up com aviso
        tkinter.messagebox.showinfo(title="Usuários cadastrados",message="Não existe nenhum usuário cadastrado.")

FONTEGRANDE = ("Cambria", 35) # constante com o tipo da fonte e tamanho que utilizaremos para os títulos das páginas
  
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
         
        # criando container
        container = tk.Frame(self)  
        container.pack(side = "top", fill = "both", expand = True) 
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # definindo estilo personalizado para alguns botões
        style = ttk.Style()
        style.map("BotaoVermelho.TButton",
          background = [("active", "red"), ("!active", "red")],
          foreground = [("active", "black"), ("!active", "black")])
        
        style.map("BotaoVerde.TButton",
          background = [("active", "green"), ("!active", "green")],
          foreground = [("active", "black"), ("!active", "black")])

        # dicionário com todas as páginas do programa
        self.frames = {}  
        for F in (Inicial, CadastroLivros, CadastroUsuarios, EmprestimoLivros, DevolucaoLivros, ConsultaLivros, Relatorios):
            frame = F(container, self)
            self.frames[F] = frame 
            frame.grid(row = 0, column = 0, sticky ="nsew")
        # colocando a página Inicial no topo de todas as outras páginas criadas
        self.show_frame(Inicial)
    # função para poder trocar as páginas
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

  
class Inicial(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
         
        # criando a label para o Título
        titulo = ttk.Label(self, text ="Menu Inicial", font = FONTEGRANDE)
        # posicionando o título utilizando o método grid, faremos isso para todos os elementos
        titulo.grid(row = 0, column = 2, padx = 10, pady = (0, 10)) 
  
        button1 = ttk.Button(self, text ="Cadastrar Livros", # botão de cadastrar livros
        command = lambda : controller.show_frame(CadastroLivros)) # comando para trocar de página
        button1.grid(row = 1, column = 1, padx = 10, pady = (0, 10)) # alinhando o botão em linha e coluna
        # os botões abaixo segue o mesmo padrão do botão acima
        button2 = ttk.Button(self, text ="Cadastrar Usuários",
        command = lambda : controller.show_frame(CadastroUsuarios))
        button2.grid(row = 1, column = 2, padx = 10, pady = (0, 10))

        button3 = ttk.Button(self, text ="Empréstimo de Livros",
        command = lambda : controller.show_frame(EmprestimoLivros))
        button3.grid(row = 1, column = 3, padx = 10, pady = (0, 10))
  
        button4 = ttk.Button(self, text ="Devolução de Livros",
        command = lambda : controller.show_frame(DevolucaoLivros))
        button4.grid(row = 2, column = 1, padx = 10, pady = (0, 10))
  
        button5 = ttk.Button(self, text ="Consulta de Livros",
        command = lambda : controller.show_frame(ConsultaLivros))
        button5.grid(row = 2, column = 2, padx = 10, pady = (0, 10))
  
        button6 = ttk.Button(self, text ="Relatórios",
        command = lambda : controller.show_frame(Relatorios)) 
        button6.grid(row = 2, column = 3, padx = 10, pady = (0, 10))
  

class CadastroLivros(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # criando o título (padrão de todas as páginas)
        label = ttk.Label(self, text ="Cadastrar Livros", font = FONTEGRANDE)
        label.grid(row = 0, columnspan=2, padx = 10, pady = (0, 10))

        # criando a caixa para inserir o texto (padrão de todas as páginas)
        texto = ttk.Label(self, text="Título do Livro") # criando o label do título
        texto.grid(row=1, column=0, padx = 10) # alinhando o título da caixa
        titulo_livro = ttk.Entry(self, width=50) # criando a caixa de entrada
        titulo_livro.grid(row=2, column=0, padx = 10, pady = (0, 10)) # alinhando a caixa
        # todos abaixo segue o mesmo padrão
        texto = ttk.Label(self, text="Nome do Autor")
        texto.grid(row=1, column=1, padx = 10)
        nome_autor = ttk.Entry(self, width=50)
        nome_autor.grid(row=2, column=1, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Ano de Publicação")
        texto.grid(row=3, column=0, padx = 10)
        ano_publicacao = ttk.Entry(self, width=50)
        ano_publicacao.grid(row=4, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Quantidade")
        texto.grid(row=3, column=1, padx = 10)
        qtd_livros = ttk.Entry(self, width=50)
        qtd_livros.grid(row=4, column=1, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="ID")
        texto.grid(row=5, column=0, padx = 10)
        id_livros = ttk.Entry(self, width=50)
        id_livros.grid(row=6, column=0, padx = 10, pady = (0, 10))
        
        # criando o botão para poder registrar o cadastro, passando os parâmetros necessários para a função
        botao_cadastrar = ttk.Button(self, text="Cadastrar", style='BotaoVerde.TButton',
                                     command = lambda : cadastrar_livros(titulo_livro, nome_autor,
                                                                         ano_publicacao, qtd_livros, id_livros))
        botao_cadastrar.grid(row=5, column=1, padx = 10, pady = (0, 10)) # alinhando o botão

        # criando o botão para voltar para a página inicial (padrão para todos os outras páginas)
        botao_inicio = ttk.Button(self, text ="Inicio", style='BotaoVermelho.TButton',
                            command = lambda : controller.show_frame(Inicial))
        botao_inicio.grid(row = 6, column = 1, padx = 10, pady = (0, 10))
  

# third window frame page2
class CadastroUsuarios(tk.Frame): 
    def __init__(self, parent, controller):
        # titulo padrão
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Cadastrar Usuários", font = FONTEGRANDE)
        label.grid(row = 0, columnspan=2, padx = 10, pady = (0, 10))

        # criando a caixa para inserir o texto (padrão)
        texto = ttk.Label(self, text="Nome")
        texto.grid(row=1, column=0, padx = 10)
        nome_usuario = ttk.Entry(self, width=50)
        nome_usuario.grid(row=2, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Número de identificação")
        texto.grid(row=1, column=1, padx = 10)
        numero_identificacao = ttk.Entry(self, width=50)
        numero_identificacao.grid(row=2, column=1, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Número do Telefone")
        texto.grid(row=3, column=0, padx = 10)
        numero_telefone = ttk.Entry(self, width=50)
        numero_telefone.grid(row=4, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Email")
        texto.grid(row=3, column=1, padx = 10)
        email = ttk.Entry(self, width=50)
        email.grid(row=4, column=1, padx = 10, pady = (0, 10))

        # criando o botão para poder registrar o cadastro, passando os parâmetros necessários para a função
        botao_cadastrar = ttk.Button(self, text="Cadastrar", style='BotaoVerde.TButton',
                                     command = lambda : cadastrar_usuarios(nome_usuario, numero_identificacao, numero_telefone, email))
        botao_cadastrar.grid(row=5, column=1, padx = 10, pady = (0, 10))
        # criando botão para a página inicial
        botao_inicio = ttk.Button(self, text ="Inicio", style='BotaoVermelho.TButton',
                            command = lambda : controller.show_frame(Inicial))
        botao_inicio.grid(row = 5, column = 0, padx = 10, pady = (0, 10))


class EmprestimoLivros(tk.Frame): 
    def __init__(self, parent, controller):
        # titulo padrão
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Empréstimo de Livros", font = FONTEGRANDE)
        label.grid(row = 0, columnspan=2, padx = 10, pady = (0, 10))

        # criando a caixa para inserir o texto (padrão)
        texto = ttk.Label(self, text="ID do Usuário")
        texto.grid(row=1, column=0, padx = 10)
        id_usuario = ttk.Entry(self, width=50)
        id_usuario.grid(row=2, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="ID do Livro")
        texto.grid(row=1, column=1, padx = 10)
        id_livro = ttk.Entry(self, width=50)
        id_livro.grid(row=2, column=1, padx = 10, pady = (0, 10))

        # criando o botão para poder registrar o cadastro, passando os parâmetros necessários para a função
        botao_emprestimo = ttk.Button(self, text="Registrar Empréstimo", style='BotaoVerde.TButton',
                                      command = lambda : emprestimo_livros(id_usuario, id_livro))
        botao_emprestimo.grid(row=5, column=1, padx = 10, pady = (0, 10))
        # criando botão para a página inicial
        botao_inicio = ttk.Button(self, text ="Inicio", style='BotaoVermelho.TButton',
                            command = lambda : controller.show_frame(Inicial))
        botao_inicio.grid(row = 5, column = 0, padx = 10, pady = (0, 10))


class DevolucaoLivros(tk.Frame): 
    def __init__(self, parent, controller):
        # titulo padrão
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Devolução de Livros", font = FONTEGRANDE)
        label.grid(row = 0, columnspan=2, padx = 10, pady = (0, 10))

        # criando a caixa para inserir o texto (padrão)
        texto = ttk.Label(self, text="ID do Usuário")
        texto.grid(row=1, column=0, padx = 10)
        id_usuario = ttk.Entry(self, width=50)
        id_usuario.grid(row=2, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="ID do Livro")
        texto.grid(row=1, column=1, padx = 10)
        id_livro = ttk.Entry(self, width=50)
        id_livro.grid(row=2, column=1, padx = 10, pady = (0, 10))
        # criando o botão para poder registrar o cadastro, passando os parâmetros necessários para a função
        botao_devolucao = ttk.Button(self, text="Devolução", style='BotaoVerde.TButton',
                                     command = lambda: devolucao_livros(id_usuario, id_livro))
        botao_devolucao.grid(row=5, column=1, padx = 10, pady = (0, 10))
        # criando botão para a página inicial
        botao_inicio = ttk.Button(self, text ="Inicio", style='BotaoVermelho.TButton',
                            command = lambda : controller.show_frame(Inicial))
        botao_inicio.grid(row = 5, column = 0, padx = 10, pady = (0, 10))


class ConsultaLivros(tk.Frame): 
    def __init__(self, parent, controller):
        # titulo padrão
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Consultar Livros", font = FONTEGRANDE)
        label.grid(row = 0, columnspan=2, padx = 10, pady = (0, 10))
        # criando a caixa para inserir o texto (padrão)
        texto = ttk.Label(self, text="Título")
        texto.grid(row=1, column=0, padx = 10)
        titulo_livro = ttk.Entry(self, width=50)
        titulo_livro.grid(row=2, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Nome do Autor")
        texto.grid(row=1, column=1, padx = 10)
        nome_autor = ttk.Entry(self, width=50)
        nome_autor.grid(row=2, column=1, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="Ano de Publicação")
        texto.grid(row=3, column=0, padx = 10)
        ano_publicacao = ttk.Entry(self, width=50)
        ano_publicacao.grid(row=4, column=0, padx = 10, pady = (0, 10))

        texto = ttk.Label(self, text="ID")
        texto.grid(row=3, column=1, padx = 10)
        id_livro = ttk.Entry(self, width=50)
        id_livro.grid(row=4, column=1, padx = 10, pady = (0, 10))
        # criando o botão para poder registrar o cadastro, passando os parâmetros necessários para a função
        botao_cadastrar = ttk.Button(self, text="Consultar", style='BotaoVerde.TButton',
                                     command = lambda : consultar_livros(titulo_livro, nome_autor, ano_publicacao, id_livro))
        botao_cadastrar.grid(row=5, column=1, padx = 10, pady = (0, 10))
        # criando botão para a página inicial
        botao_inicio = ttk.Button(self, text ="Inicio", style='BotaoVermelho.TButton',
                            command = lambda : controller.show_frame(Inicial))
        botao_inicio.grid(row = 5, column = 0, padx = 10, pady = (0, 10))
  
  
class Relatorios(tk.Frame): 
    def __init__(self, parent, controller):
        # titulo padrão
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Relatórios", font = FONTEGRANDE)
        label.grid(row = 0, columnspan=3, padx = 10, pady = (0, 10))

        # criando botão paga gerar relatório de livros disponíveis
        botao_livros_disponiveis = ttk.Button(self, text="Livros Disponíveis",
                                              command = lambda : livros_disponiveis())
        botao_livros_disponiveis.grid(row=1, column=0, padx = 10, pady = (0, 10))

        # criando botão paga gerar relatório de livros emprestados
        botao_livros_emprestados = ttk.Button(self, text="Livros Emprestados",
                                              command = lambda : livros_emprestados())
        botao_livros_emprestados.grid(row=1, column=1, padx = 10, pady = (0, 10))

        # criando botão paga gerar relatório de usuários cadastrados
        botao_usuarios_cadastrados = ttk.Button(self, text="Usuários Cadastrados",
                                                command = lambda : usuarios_cadastrados())
        botao_usuarios_cadastrados.grid(row=1, column=2, padx = 10, pady = (0, 10))

        # criando botão para a página inicial
        botao_inicio = ttk.Button(self, text ="Inicio", style='BotaoVermelho.TButton',
                            command = lambda : controller.show_frame(Inicial))
        botao_inicio.grid(row = 2, column = 1, padx = 10, pady = (0, 10))
  
  
# Inicializando a interface gráfica Tkinter
app = App()
app.title("Gerenciamento de Biblioteca") #adicionar título ao programa
app.mainloop() #manter em loop até fechar a janela

# Fechar a conexão com o pyodbc logo após de fechar a janela do programa
cursor.close()
conexao.close()
