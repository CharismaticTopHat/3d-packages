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

packer.add_bin(Bin("large-2-box", 10.6875, 5.75, 10.0, 70.0))

packer.add_item(Item("50g [powder 1]", 3.9370, 1.9685, 1.9685, 1.0))
packer.add_item(Item("50g [powder 2]", 3.9370, 1.9685, 1.9685, 1.0))
packer.add_item(Item("50g [powder 3]", 3.9370, 1.9685, 1.9685, 1.0))
packer.add_item(Item("250g [powder 4]", 7.8740, 3.9370, 1.9685, 1.0))
packer.add_item(Item("250g [powder 5]", 7.8740, 3.9370, 1.9685, 1.0))
packer.add_item(Item("250g [powder 6]", 7.8740, 3.9370, 1.9685, 1.0))
packer.add_item(Item("250g [powder 7]", 7.8740, 3.9370, 1.9685, 1.0))
packer.add_item(Item("250g [powder 8]", 7.8740, 3.9370, 1.9685, 1.0))
packer.add_item(Item("250g [powder 9]", 7.8740, 3.9370, 1.9685, 1.0))

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
    width::Float64 = 0.0
    height::Float64 = 0.0
    depth::Float64 = 0.0
end

@agent struct storage(GridAgent{2})
    name::String
    boxes::Vector{box} = []
end

# Buscar la caja más cercana elegible
function closest_box_nearby(agent::robot, model)
    closest_box = nothing
    min_distance = Inf

    for neighbor in allagents(model)
        if isa(neighbor, box) && neighbor.status == waiting && does_box_fit(neighbor.name, neighbor.assigned_storage, packer)
            dist_to_neighbor = abs(neighbor.pos[1] - agent.pos[1]) + abs(neighbor.pos[2] - agent.pos[2])
            if dist_to_neighbor < min_distance
                min_distance = dist_to_neighbor
                closest_box = neighbor
            end
        end
    end
    return closest_box, min_distance
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


# Función para encontrar el almacenamiento más cercano usando distancia Manhattan
function closest_storage_nearby(agent::robot, model)
    closest_storage = nothing
    min_distance = Inf

    for neighbor in allagents(model)
        if isa(neighbor, storage)
            if neighbor.boxes != 0
                dist_to_neighbor = abs(neighbor.pos[1] - agent.pos[1]) + abs(neighbor.pos[2] - agent.pos[2])
                if dist_to_neighbor < min_distance
                    min_distance = dist_to_neighbor
                    closest_storage = neighbor
                end
            end
        end
    end
    return closest_storage, min_distance
end

# Verifica si otro coche ya está en la posición de destino
function detect_collision(agent::robot, target_pos, model)
    for neighbor in allagents(model)
        if isa(neighbor, robot) && neighbor !== agent
            if neighbor.pos == target_pos
                return true
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

# Intenta moverse a la nueva posición si no hay colisión y no es una zona restringida
function try_move!(agent::robot, model, dx::Int, dy::Int, griddims)
    current_pos = agent.pos
    new_position = (current_pos[1] + dx, current_pos[2] + dy)
    agent.nextPos = (new_position[1], new_position[2])
    
    if new_position[2] == griddims[2]
        return false
    end

    if !detect_collision(agent, new_position, model)
        move_agent!(agent, new_position, model)
        update_orientation_and_counter!(agent, dx, dy)  # Update orientation for any movement
        return true
    else
        return false
    end
end

# Determina las dependencias físicas (cajas encima)
function calculate_dependencies!(model)
    for b in allagents(model)
        if isa(b, box)
            for other in allagents(model)
                if isa(other, box) && b !== other
                    # Considera como "encima" si están en la misma posición X/Y y el otro tiene menor profundidad
                    if b.pos[1] == other.pos[1] && b.pos[2] == other.pos[2] && b.depth < other.depth
                        push!(b.depends_on, other.name)
                    end
                end
            end
        end
    end
end

# Función para verificar si una caja está lista para ser recolectada
function is_ready_to_collect(agent::box, model)
    return isempty(agent.depends_on) || all(dep -> find_agent_by_name(dep, model).status == delivered, agent.depends_on) || all(dep -> find_agent_by_name(dep, model).status == taken, agent.depends_on)
end

# Modificar la lógica del paso del robot para que las cajas sigan a los RobotStatus
function agent_step!(agent::robot, model, griddims)
    # Si el robot está vacío, busca una caja elegible para recoger
    if agent.capacity == empty
        closest_box, _ = closest_box_nearby(agent, model)

        if closest_box !== nothing
            # Dirígete hacia la caja
            move_towards!(agent, closest_box.pos, model, griddims)
            if agent.pos === closest_box.pos
                closest_box.status = taken
                agent.capacity = full
                agent.carried_box = closest_box
            end
        else
            return
        end
    elseif agent.capacity == full
        # Actualiza la posición de la caja que transporta
        if agent.carried_box !== nothing
            agent.carried_box.pos = agent.pos  # La caja sigue al robot
        end

        # Lógica para entregar la caja en el almacenamiento más cercano
        closest_storage, _ = closest_storage_nearby(agent, model)
        if closest_storage !== nothing
            move_towards!(agent, closest_storage.pos, model, griddims)
            if is_adjacent(agent.pos, closest_storage.pos)
                deliver_box_in_front!(agent, model, closest_storage)
                return_to_initial_x!(agent, model, griddims)
            end
        end
    end
end


# Función para que el robot entregue la caja en el almacenamiento
function deliver_box_in_front!(Robot::robot, model, Storage::storage)
    if Robot.carried_box !== nothing
        delivered_box = Robot.carried_box
        push!(Storage.boxes, delivered_box)  # Añadir la caja al almacenamiento
        delivered_box.status = delivered    # Marcar la caja como entregada
        delivered_box.pos = Storage.pos     # Actualizar la posición de la caja al almacenamiento
        Robot.carried_box = nothing         # El robot deja de transportar la caja
        Robot.capacity = empty              # Marcar al robot como vacío
    end
end


# Función auxiliar para verificar si dos posiciones son adyacentes (sin diagonal)
function is_adjacent(pos1, pos2)
    return (pos1[1] == pos2[1] && abs(pos1[2] - pos2[2]) == 1) || (pos1[2] == pos2[2] && abs(pos1[1] - pos2[1]) == 1)
end

function any_box_nearby(agent::robot, model, griddims)
    radius = griddims[2] / 10
    for neighbor in nearby_agents(agent, model, radius)
        if isa(neighbor, box) && neighbor.status == waiting
            return true
        end
    end
    return false
end

function return_to_initial_x!(agent::robot, model, griddims)
    current_x = agent.pos[1]
    target_x = agent.initial_x
    if current_x != target_x
        move_towards!(agent, (target_x, agent.pos[2]), model, griddims)
    end
end

function deliver_box_in_front!(Robot::robot, model, Storage::storage)
    if Robot.carried_box !== nothing
        delivered_box = Robot.carried_box
        push!(Storage.boxes, delivered_box)  # Add the box to the storage
        delivered_box.status = delivered  # Mark the box as delivered
        Robot.carried_box = nothing  # Clear the robot's carried box
        Robot.capacity = empty  # Set robot capacity to empty
    end
end


# Mover hacia una posición objetivo sin entrar en la última fila
function move_towards!(agent::robot, target_pos, model, griddims)
    current_pos = agent.pos
    diff_x = target_pos[1] - current_pos[1]
    diff_y = target_pos[2] - current_pos[2]

    # Determina direcciones primaria y secundaria
    primary, secondary = if abs(diff_x) > abs(diff_y)
        ((sign(diff_x), 0), (0, sign(diff_y)))
    else
        ((0, sign(diff_y)), (sign(diff_x), 0))
    end

    # Intenta la dirección primaria sin entrar en la última fila
    if (current_pos[2] + primary[2]) < griddims[2] && try_move!(agent, model, primary[1], primary[2], griddims)
        # Movimiento exitoso
        update_orientation_and_counter!(agent, primary[1], primary[2])
    elseif (current_pos[2] + secondary[2]) < griddims[2] && try_move!(agent, model, secondary[1], secondary[2], griddims)
        # Movimiento exitoso
        update_orientation_and_counter!(agent, secondary[1], secondary[2])
    else
        println("No se encuentra manera de llegar al destino deseado. Se detendrá el agente.")
    end
end

# Funciones de paso de agente para Caja y Almacenamiento (sin acción)
function agent_step!(agent::box, model, griddims)
end

function agent_step!(agent::storage, model, griddims)
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


function initialize_model(; griddims=(80, 80), number=80, packer=packer)
    space = GridSpace(griddims; periodic = false, metric = :manhattan)
    model = ABM(Union{robot, box, storage}, space; agent_step! = (a, m) -> agent_step!(a, m, griddims), scheduler = Schedulers.fastest)

    all_positions = [(x, y) for x in 1:griddims[1], y in 1:griddims[2]-1]
    shuffled_positions = shuffle(all_positions)

    # Configurar robots
    num_robots = 5
    bottom_y = griddims[2]
    initial_position = div(griddims[1], 10)
    spacing = 2 * initial_position

    robot_columns = [initial_position + (i-1) * spacing for i in 1:num_robots]
    robot_positions = [(col, bottom_y) for col in robot_columns]
    for robot_pos in robot_positions
        add_agent!(robot, model; pos = robot_pos, initial_x = robot_pos[1])
    end

    # Configurar almacenamiento basado en el empaquetador
    if packer !== nothing
        packer_bins = packer[:bins]
        storage_positions = [(x, griddims[2]) for x in 1:griddims[1] if x % 5 == 0]
        for (i, bin) in enumerate(packer_bins)
            pos = storage_positions[i % length(storage_positions) + 1]
            add_agent!(storage, model; pos = pos, name = bin[:name])
        end

        # Añadir todas las cajas (aptas e inapropiadas)
        all_items = packer[:items]
        for (i, item) in enumerate(all_items)
            container_name = assigned_boxes[item[:name]]
            pos = shuffled_positions[i % length(shuffled_positions) + 1]
            add_agent!(box, model;
                pos = pos,
                name = item[:name],
                container = container_name,
                assigned_storage = container_name
            )
        end
    else
        error("El empaquetador es obligatorio para esta lógica.")
    end

    calculate_dependencies!(model)

    return model
end
