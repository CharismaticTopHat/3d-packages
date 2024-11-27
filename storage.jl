using Agents, Random
using StaticArrays: SVector
using Dates
using PyCall

#Python code
#from py3dbp import Packer, Bin, Item
Packer = pyimport("py3dbp").Packer
Bin = pyimport("py3dbp").Bin
Item = pyimport("py3dbp").Item

packer = Packer()

packer.add_bin(Bin("large-2-box", 320, 200, 220, 3200.0))

packer.add_item(Item("Letter", 70.0000, 70.0000, 70.0000, 5.0))
packer.add_item(Item("Bowling Ball", 50.0000, 50.0000, 50.0000 , 100.0))
packer.add_item(Item("Poster", 50.0000, 50.0000, 50.0000, 8.0))
packer.add_item(Item("Cat Tower", 70.0000, 70.0000, 70.0000, 130.0))
packer.add_item(Item("Console", 50.0000, 50.0000, 50.0000, 40.0))
packer.add_item(Item("Glass Bottle", 10.0000, 10.0000, 10.0000, 3.0))
packer.add_item(Item("TV", 70.0000, 70.0000, 70.0000, 180.0))
packer.add_item(Item("Painting", 50.0000, 50.0000, 50.0000, 50.0))
packer.add_item(Item("Phone", 10.0000, 10.0000, 10.0000, 10.0))
packer.add_item(Item("Lego Set", 50.0000, 50.0000, 50.0000, 20.0))
packer.add_item(Item("Couch", 70.0000, 70.0000, 70.0000, 400.0))
packer.add_item(Item("Table", 70.0000, 70.0000, 70.0000, 600.0))
packer.add_item(Item("Microwave", 50.0000, 50.0000, 50.0000, 40.0))
packer.add_item(Item("Tablet", 10.0000, 10.0000, 10.0000, 13.0))
packer.add_item(Item("Chair", 50.0000, 50.0000, 50.0000, 80.0))

packer.pack()

for b in packer[:bins]
    println("::::::::::: ", b[:string]())

    println("FITTED ITEMS:")
    for item in b[:items]
        println("====> ", item[:string]())
    end

    println("UNFITTED ITEMS:")
    for item in b[:unfitted_items]
        println("====> ", item[:string]())
    end

    println("***************************************************")
    println("***************************************************")
end

assigned_boxes = Dict{String, String}()
assigned_boxes = Dict{String, String}()
for b in packer[:bins]
    # Assign fitted items
    for item in b[:items]
        assigned_boxes[item[:name]] = b[:name]
    end
    # Assign unfitted items with a special label (e.g., "Unfitted")
    for item in b[:unfitted_items]
        assigned_boxes[item[:name]] = b[:name]
    end
end

# Definición de Enums
@enum BoxStatus waiting taken delivered
@enum RobotStatus empty full
@enum Movement moving stop

# Constantes de Orientación en Radianes
orient_up = 0
orient_left = 1
orient_down = 2
orient_right = 3

@agent struct box(GridAgent{2})
    name::String
    status::BoxStatus = waiting
    container::String  # Original container field
    assigned_storage::String  # Storage name to which the box should be delivered
    depends_on::Vector{String} = []  # Dependencias (cajas que deben entregarse primero)
    width::Float64 = 0.0
    height::Float64 = 0.0
    depth::Float64 = 0.0
    truckCoords::Tuple{Float64, Float64} = (0.0, 0.0)
    finalZ::Float64 = 0.0
end

@agent struct robot(GridAgent{2}) 
    capacity::RobotStatus = empty
    orientation::Float64 = orient_right
    carried_box::Union{box, Nothing} = nothing
    initial_x::Int = 0
    stopped::Movement = moving
    counter::Int = 0
    nextPos::Tuple{Float64, Float64} = (0.0, 0.0)
    dx::Int = 0
    dy::Int = 0
    target_box::Union{box, Nothing} = nothing  # Caja asignada al robot
    assigned_boxes::Vector{String} = []  # Cajas asignadas al robot
    current_index::Int = 1  # Índice actual en el arreglo assigned_boxes
end

@agent struct storage(GridAgent{2})
    name::String
    boxes::Vector{box} = []
    width::Float64 = 0.0
    height::Float64 = 0.0
    depth::Float64 = 0.0
end

# Verificar si una caja es apta
function does_box_fit(box_name::String, storage_name::String, packer)
    for bin in packer[:bins]
        if bin[:name] == storage_name
            for fitted_item in bin[:items]
                if fitted_item[:name] == box_name
                    return true
                end
            end
        end
    end
    return false
end

function update_orientation_and_counter!(agent::robot, dx::Int, dy::Int)
    new_orientation = agent.orientation
    if dx == 1
        new_orientation = orient_right
        agent.dx = dx
    elseif dx == -1
        new_orientation = orient_left
        agent.dx = dx
    elseif dy == 1
        new_orientation = orient_up
        agent.dy = dy
    elseif dy == -1
        new_orientation = orient_down
        agent.dy = dy
    end

    if agent.orientation != new_orientation
        if (agent.orientation == orient_up && new_orientation == orient_down) ||
            (agent.orientation == orient_left && new_orientation == orient_right) ||
            (agent.orientation == orient_down && new_orientation == orient_up) ||
            (agent.orientation == orient_right && new_orientation == orient_left)
            agent.counter = 18 
        else
            agent.counter = 9
        end
        agent.orientation = new_orientation
    end
end
# Actualiza la orientación del coche según la dirección de movimiento
function update_orientation!(agent::robot, dx::Int, dy::Int)
    if dx == 1
        agent.orientation = orient_right
    elseif dx == -1
        agent.orientation = orient_left
    elseif dy == 1
        agent.orientation = orient_up
    elseif dy == -1
        agent.orientation = orient_down
    end
end

# Function to check if a position is valid within grid dimensions
function valid_position(pos::Tuple{Int, Int}, griddims::Tuple{Int, Int})
    x, y = pos
    max_x, max_y = griddims
    return x > 0 && x <= max_x && y > 0 && y <= max_y
end

function try_move!(agent::robot, model, dx::Int, dy::Int, griddims)
    current_pos = agent.pos
    new_position = (current_pos[1] + dx, current_pos[2] + dy)

    # Detectar robots como obstáculos
    obstacles = Set()
    for neighbor in allagents(model)
        if isa(neighbor, robot) && neighbor !== agent
            push!(obstacles, neighbor.pos)
        end
    end

    # Verificar si la nueva posición es válida y no está ocupada
    if valid_position(new_position, griddims) && !(new_position in obstacles)
        move_agent!(agent, new_position, model)
        update_orientation_and_counter!(agent, dx, dy)
        return true
    else
        # Intentar rutas alternativas
        println("Robot $(agent.id) encuentra obstáculo en la posición $new_position. Buscando ruta alternativa.")

        # Generar direcciones alternativas
        alternative_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        shuffle!(alternative_directions)

        for (alt_dx, alt_dy) in alternative_directions
            alt_position = (current_pos[1] + alt_dx, current_pos[2] + alt_dy)

            if valid_position(alt_position, griddims) && !(alt_position in obstacles)
                move_agent!(agent, alt_position, model)
                update_orientation_and_counter!(agent, alt_dx, alt_dy)
                println("Robot $(agent.id) se movió a $alt_position para evitar obstáculos.")
                return true
            end
        end

        println("Robot $(agent.id) no encontró ruta alternativa y permanece en su lugar.")
        return false
    end
end

function get_next_box_in_order(current_box_name::Union{String, Nothing}, packer, model)
    found_current = current_box_name === nothing  # Flag para iniciar la búsqueda
    for bin in packer[:bins]
        for item in bin[:items]
            # Si encontramos la caja actual, el siguiente elemento será el próximo objetivo
            if found_current
                next_box = find_agent_by_name(item[:name], model)
                if next_box !== nothing && next_box.status == waiting
                    return next_box
                end
            end
            if item[:name] == current_box_name
                found_current = true
            end
        end
    end
    return nothing
end

function assign_next_box(packer, model, box_index_ref::Base.RefValue{Int})
    all_boxes = [item[:name] for bin in packer[:bins] for item in bin[:items]]
    while box_index_ref[] <= length(all_boxes)
        next_box_name = all_boxes[box_index_ref[]]
        box_index_ref[] += 1  # Avanza el índice local

        # Verifica si la caja está disponible en el modelo
        next_box_agent = find_agent_by_name(next_box_name, model)
        if next_box_agent !== nothing && next_box_agent.status == waiting
            return next_box_agent
        end
    end
    return nothing  # No hay más cajas disponibles
end

function agent_step!(agent::robot, model, griddims, box_index_ref::Base.RefValue{Int})
    # Si no hay más cajas asignadas
    if agent.target_box === nothing && agent.capacity == empty
        # Dirígete a la zona de espera (fila superior del grid)
        target_position = (agent.pos[1], 1)  # Fila superior
        move_towards!(agent, target_position, model, griddims)
        
        if agent.pos[2] == 1
            agent.stopped = stop  # Marca al robot como detenido en la zona de espera
        end
        return
    end

    if agent.capacity == empty
        # Dirígete hacia la caja asignada
        if agent.target_box !== nothing
            move_towards!(agent, agent.target_box.pos, model, griddims)
            if agent.pos === agent.target_box.pos
                agent.target_box.status = taken
                agent.capacity = full
                agent.carried_box = agent.target_box
            end
        end
    elseif agent.capacity == full
        # Actualiza la posición de la caja que transporta
        if agent.carried_box !== nothing
            agent.carried_box.pos = agent.pos  # La caja sigue al robot
        end

        # Verifica si las dependencias de la caja han sido entregadas
        assigned_storage_name = agent.carried_box.assigned_storage
        storage_agent = find_agent_by_name(assigned_storage_name, model)

        if storage_agent !== nothing
            dist_to_storage = abs(agent.pos[1] - storage_agent.pos[1]) + abs(agent.pos[2] - storage_agent.pos[2])
            
            if !all(dep -> find_agent_by_name(dep, model).status == delivered, agent.carried_box.depends_on)
                if dist_to_storage <= 8
                    println("El robot $(agent.id) está dentro del radio de 4 del almacenamiento para la caja $(agent.carried_box.name). Moviéndose temporalmente hacia arriba.")
                    return  # Detente hasta que las dependencias se cumplan
                else
                    println("El robot $(agent.id) sigue trabajando ya que está fuera del radio de espera para la caja $(agent.carried_box.name).")
                end
            end
        end

        # Intenta entregar la caja al almacenamiento asignado
        if storage_agent !== nothing
            move_towards!(agent, storage_agent.pos, model, griddims)
            if is_adjacent(agent.pos, storage_agent.pos)
                deliver_box_in_front!(agent, model, storage_agent)

                # Asignar nueva caja al robot o enviarlo a la zona de espera
                agent.target_box = assign_next_box(packer, model, box_index_ref)
                if agent.target_box === nothing
                    println("El robot $(agent.id) no tiene más cajas asignadas y se dirige a la zona de espera.")
                end
                agent.carried_box = nothing
                agent.capacity = empty
            end
        end
    end
end

# Una única versión para deliver_box_in_front!
function deliver_box_in_front!(Robot::robot, model, Storage::storage)
    if Robot.carried_box !== nothing
        delivered_box = Robot.carried_box
        push!(Storage.boxes, delivered_box)  # Añadir la caja al almacenamiento
        delivered_box.status = delivered    # Marcar como entregada
        delivered_box.pos = delivered_box.truckCoords     # Actualizar la posición
        println("La caja {}")
        Robot.carried_box = nothing         # Limpiar el robot
        Robot.capacity = empty              # Marcar el robot como vacío
    end
end

function find_agent_pos_by_name(name::String, model, packer)
    # Retrieve the corresponding item from the packer bins
    for bin in packer[:bins]
        for item in bin[:items]
            if item[:name] == name
                # Update the position of the corresponding box agent in the model
                for agent in allagents(model)
                    if isa(agent, box) && agent.name == name
                        agent.pos = (item[:position][:x], item[:position][:y]) # Assuming 2D positions
                        # No need to return anything here, the position is updated
                    end
                end
            end
        end
    end
end

# Función auxiliar para verificar si dos posiciones son adyacentes (sin diagonal)
function is_adjacent(pos1, pos2)
    return (pos1[1] == pos2[1] && abs(pos1[2] - pos2[2]) == 1) || (pos1[2] == pos2[2] && abs(pos1[1] - pos2[1]) == 1)
end

# Implementación de A* (A-star) sin librerías externas
function find_path(start_pos, end_pos, obstacles, griddims)
    open_set = [start_pos]  # Lista de nodos abiertos (por explorar)
    came_from = Dict()  # Rastrear el camino para reconstruirlo
    g_score = Dict(start_pos => 0)  # Coste desde el inicio hasta el nodo
    f_score = Dict(start_pos => manhattan_distance(start_pos, end_pos))  # Coste total estimado

    while !isempty(open_set)
        # Encuentra el nodo con menor f_score
        current = open_set[argmin([get(f_score, pos, Inf) for pos in open_set])]

        # Si llegamos al destino, reconstruimos el camino
        if current == end_pos
            return reconstruct_path(came_from, current)
        end

        # Remueve el nodo actual de la lista de abiertos
        deleteat!(open_set, findfirst(x -> x == current, open_set))

        # Explora vecinos
        for neighbor in get_neighbors(current, griddims)
            if neighbor in obstacles
                continue  # Salta si es un obstáculo
            end

            tentative_g_score = get(g_score, current, Inf) + 1  # El coste al vecino

            if tentative_g_score < get(g_score, neighbor, Inf)
                # Este camino es mejor, actualizamos las estructuras
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, end_pos)

                # Añadimos a la lista de abiertos si no está ya
                if neighbor ∉ open_set
                    push!(open_set, neighbor)
                end
            end
        end
    end

    return []  # Si no hay camino, devolvemos una lista vacía
end

# Distancia Manhattan para calcular heurística
function manhattan_distance(pos1, pos2)
    return abs(pos1[1] - pos2[1]) + abs(pos1[2] - pos2[2])
end

# Reconstrucción del camino desde `came_from`
function reconstruct_path(came_from, current)
    path = [current]
    while current in keys(came_from)
        current = came_from[current]
        push!(path, current)
    end
    return reverse(path)
end

# Obtener vecinos válidos de una posición
function get_neighbors(pos, griddims)
    neighbors = [(pos[1] + dx, pos[2] + dy) for (dx, dy) in [(1, 0), (-1, 0), (0, 1), (0, -1)]]
    return filter(x -> valid_position(x, griddims), neighbors)
end

# Buscar una posición disponible en x para y = 1
function find_available_x(y, griddims, model)
    available_positions = []
    for x in 1:griddims[1]
        pos = (x, y)
        if !is_position_occupied(pos, model)
            push!(available_positions, pos)
        end
    end
    return isempty(available_positions) ? nothing : rand(available_positions)  # Devuelve una aleatoria o `nothing`
end

# Detectar si la posición está ocupada por otro robot
function is_position_occupied(pos, model)
    for neighbor in allagents(model)
        if isa(neighbor, robot) && neighbor.pos == pos
            return true
        end
    end
    return false
end

# Modificar move_towards! para manejar casos en y = 1
function move_towards!(agent::robot, target_pos, model, griddims)
    current_pos = agent.pos

    # Detectar obstáculos (otros robots)
    obstacles = Set([neighbor.pos for neighbor in allagents(model) if isa(neighbor, robot) && neighbor !== agent])

    # Calcular ruta usando A*
    path = find_path(current_pos, target_pos, obstacles, griddims)
    
    # Validar el contenido de `path`
    if isempty(path)
        println("Robot $(agent.id): No se encontró ruta válida hacia $target_pos.")

        # Si el destino está en y = 1, buscar otra posición válida en x
        if target_pos[2] == 1
            new_target_pos = find_available_x(1, griddims, model)
            if new_target_pos !== nothing
                println("Robot $(agent.id): Moviéndose a una nueva posición disponible $new_target_pos en y = 1.")
                move_towards!(agent, new_target_pos, model, griddims)
            else
                println("Robot $(agent.id): No hay posiciones disponibles en y = 1.")
            end
        end
        return
    elseif length(path) == 1
        println("Robot $(agent.id): Ya está en la posición objetivo $current_pos.")
        return
    end

    # Mover hacia el siguiente paso en la ruta
    next_step = path[2]  # Primer paso después de la posición actual
    dx, dy = next_step[1] - current_pos[1], next_step[2] - current_pos[2]
    try_move!(agent, model, dx, dy, griddims)
end

# Funciones de paso de agente para Caja y Almacenamiento (sin acción)
function agent_step!(agent::box, model, griddims, box_index_ref::Base.RefValue{Int})
end

function agent_step!(agent::storage, model, griddims, box_index_ref::Base.RefValue{Int})
end

# Function to find an agent by its name, limited to box and storage agents
function find_agent_by_name(name::String, model)
    for agent in allagents(model)
        if isa(agent, Union{box, storage}) && agent.name == name
            return agent
        end
    end
    return nothing # Return nothing if no agent with the given name is found
end


# Modificar `calculate_dependencies!` para establecer correctamente las dependencias
function calculate_dependencies!(model, packer)
    # Iterar sobre los contenedores en el empaquetador
    for bin in packer[:bins]
        previous_box_name = nothing  # Variable para rastrear la caja anterior
        for item in bin[:items]
            # Encontrar la caja correspondiente en el modelo
            current_box = find_agent_by_name(item[:name], model)
            if current_box !== nothing
                # Si hay una caja anterior, agregarla como dependencia
                if previous_box_name !== nothing
                    push!(current_box.depends_on, previous_box_name)
                end
                # Actualizar la caja anterior
                previous_box_name = item[:name]
            end
        end
    end
end

function initialize_model(; griddims=(30, 30), number=80, packer=packer)
    box_index_ref = Ref(1)  # Índice local para esta simulación
    space = GridSpace(griddims; periodic = false, metric = :manhattan)
    model = ABM(
    Union{robot, box, storage}, space;
    agent_step! = (agent, model) -> agent_step!(agent, model, griddims, box_index_ref),
    scheduler = Schedulers.fastest
    )

    all_positions = [(x, y) for x in 1:griddims[1], y in 1:griddims[2]-1]
    shuffled_positions = shuffle(all_positions)

    # Configurar almacenamiento basado en el empaquetador
    if packer !== nothing
        packer_bins = packer[:bins]
        storage_positions = [(x, griddims[2]) for x in 1:griddims[1] if x % 5 == 0]
        for (i, bin) in enumerate(packer_bins)
            pos = storage_positions[i % length(storage_positions) + 1]
            add_agent!(storage, model; pos = pos, name = bin[:name], width = bin[:width], height = bin[:height], depth = bin[:depth])
        end

        # Añadir todas las cajas (aptas e inapropiadas)
        all_items = packer[:items]
        for (i, item) in enumerate(all_items)
            container_name = assigned_boxes[item[:name]]
            pos = shuffled_positions[i % length(shuffled_positions) + 1]
            item_coords = item[:position]
            add_agent!(box, model;
                pos = pos,
                name = item[:name],
                container = container_name,
                assigned_storage = container_name,
                width = item[:width],
                height = item[:height],
                depth = item[:depth],
                truckCoords = (item_coords[1], item_coords[2]),
                finalZ = item_coords[3]
            )
        end
    else
        error("El empaquetador es obligatorio para esta lógica.")
    end

    # Configurar robots después de agregar las cajas
    num_robots = 5
    bottom_y = griddims[2]
    initial_position = div(griddims[1], 10)
    spacing = 2 * initial_position

    robot_columns = [initial_position + (i-1) * spacing for i in 1:num_robots]
    robot_positions = [(col, bottom_y) for col in robot_columns]

    for robot_pos in robot_positions
        next_box = assign_next_box(packer, model, box_index_ref)  # Usa índice local
        add_agent!(robot, model; pos = robot_pos, initial_x = robot_pos[1], target_box = next_box)
    end

    calculate_dependencies!(model, packer)

    return model
end