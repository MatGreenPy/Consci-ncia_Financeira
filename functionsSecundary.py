import os
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('agg')

def despesasGrafico(busca, dia_filtrar, mes_filtrar, ano_filtrar, id_usuario):
    despesas_tipos = {}
    
    if id_usuario is None:
        return None

    for despesa in busca:
        despesas_tipos[despesa[0]] = despesa[1] 

    tipos = list(despesas_tipos.keys())
    valores = list(despesas_tipos.values())

    cores = ['#8B0000', '#B22222', '#FF0000', '#DC143C', '#FF6347', '#FF4500', '#FF7F7F', '#F08080', '#FA8072', '#E9967A']
    legenda = dict(zip(tipos, cores)) 

    cores_usadas = [legenda.get(tipo, '#CCCCCC') for tipo in tipos]

    plt.figure(figsize=(8, 4))  
    plt.bar(tipos, valores, color=cores_usadas)
    plt.ylabel('Valor Total')
    
  
    if dia_filtrar == '' and mes_filtrar != '' and ano_filtrar != '':
        plt.title(f'Total de despesas por tipo do mês de: {mes_filtrar} / {ano_filtrar}')
    elif dia_filtrar != '' and mes_filtrar != '' and ano_filtrar != '':
        plt.title(f'Total de despesas por tipo do dia {dia_filtrar} / {mes_filtrar} / {ano_filtrar}')
    elif dia_filtrar == '' and mes_filtrar == '' and ano_filtrar != '':
        plt.title(f'Total de despesas por tipo do ano de {ano_filtrar}')
    plt.xticks([])  
    plt.tight_layout()

 
    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in legenda.values()]
    labels = legenda.keys()
    plt.legend(handles, labels, title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left')

    file_path = os.path.join('static', 'despesas_grafico.png')
    plt.savefig(file_path, bbox_inches='tight') 
    plt.close('all')
    plt.clf()
    plt.cla()

    return file_path
