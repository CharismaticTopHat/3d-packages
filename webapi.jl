include("storage.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

# Diccionario para almacenar instancias de simulación
instances = Dict()
dynamic_boxes = []  # Lista global para almacenar cajas dinámicas

# Ruta para agregar una nueva caja
route("/boxes", method=POST) do
    payload = jsonpayload()
    name = payload["name"]
    width = payload["width"]
    height = payload["height"]
    depth = payload["depth"]
    weight = payload["weight"]

    # Crear la caja y añadirla a la lista global
    new_box = Dict(
        :name => name,
        :width => width,
        :height => height,
        :depth => depth,
        :weight => weight
    )
    push!(dynamic_boxes, new_box)

    json(Dict(:msg => "Caja agregada exitosamente", :box => new_box))
end

# Ruta para listar todas las cajas
route("/boxes", method=GET) do
    json(Dict(:boxes => dynamic_boxes))
end

# Ruta para eliminar una caja por nombre
route("/boxes/:name", method=DELETE) do
    box_name = params(:name)
    global dynamic_boxes

    # Filtrar cajas para excluir la caja con el nombre dado
    dynamic_boxes = filter(box -> box[:name] != box_name, dynamic_boxes)

    json(Dict(:msg => "Caja eliminada exitosamente", :remaining_boxes => dynamic_boxes))
end

# Ruta para iniciar una nueva simulación
route("/simulations", method=POST) do
    payload = jsonpayload()
    #x = payload["dim"][1]
    #y = payload["dim"][2]
    #number = payload["number"]

    # Incorporar las cajas dinámicas al packer
    for box in dynamic_boxes
        packer.add_item(Item(
            box[:name],
            box[:width],
            box[:height],
            box[:depth],
            box[:weight]
        ))
    end

    model = initialize_model(griddims=(300, 600), number=80, packer=packer)
    id = string(uuid1())  # Crea un identificador único para la instancia de modelo
    instances[id] = model  # Almacena el modelo en el diccionario

    # Recopila todos los agentes (cajas, coches, almacenamientos)
    boxes = []
    robots = []
    storages = []
    for agent in allagents(model)
        if agent isa box
            push!(boxes, agent)
        elseif agent isa robot
            push!(robots, agent)
        elseif agent isa storage
            push!(storages, agent)
        end
    end

    # Retorna los detalles de la simulación con el ID y agentes de la simulación
    json(Dict(:msg => "Simulación iniciada", "Location" => "/simulations/$id", "boxes" => boxes, "robots" => robots, "storages" => storages))
end

# Ruta para ejecutar la simulación con un ID específico
route("/simulations/:id", method=GET) do
    model_id = params(:id)  # Extrae el ID del modelo desde los parámetros de la URL
    model = instances[model_id]  # Recupera el modelo correspondiente del diccionario
    run!(model, 1)  # Ejecuta el modelo por un paso

    # Recopila todos los agentes (cajas, coches, almacenamientos) tras ejecutar el modelo
    boxes = []
    robots = []
    storages = []
    for agent in allagents(model)
        if agent isa box
            push!(boxes, agent)
        elseif agent isa robot
            push!(robots, agent)
        elseif agent isa storage
            push!(storages, agent)
        end
    end

    # Retorna el estado actualizado de la simulación
    json(Dict(:msg => "Paso de simulación completado", "boxes" => boxes, "robots" => robots, "storages" => storages))
end

# Configuración de CORS (Cross-Origin Resource Sharing)
Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

# Inicia el servidor de Genie
up()
