from BuildOutput import build_player_output
from Helper_Functions import update_grid
from Debugger import debug

# THIS HAS TO BE DONE DIFFERENTLY STILL, GET DATA FOR DEATHS AND TEMP
temperature = 0
death = 0


def handle_tile_placed(ctx, item):
    build_new_player_output_flag = False  # Flag to know if at the end of this handler the player output needs to be resent

    tile_id = item.get("data").get("tile_id")
    tile_type = item.get("data").get("tile_type")

    ctx.tile_manager.update_tile(tile_id, tile_type)
    uhi_array = update_grid(ctx, tile_id)

    # If the placed tile is a player tile, update accordingly
    if tile_type > 6:
        ctx.player.new_location(tile_id)
        ctx.heatmap.set_spotlight(ctx.player.get_latest_location())
        build_new_player_output_flag = True

    # If a new player location is active, send this to unity and peripherals
    if build_new_player_output_flag:
        output = build_player_output(ctx.player.get_latest_location(), ctx.tile_manager, ctx.city, temperature, death)
        ctx.server_out.send_output(output)

    debug(f"Tile of type {tile_type} PLACED at {tile_id}", "HANDLER_DEBUG")
    debug(f"UHI of new tile: {uhi_array[ctx.tile_manager.get_tile_position(tile_id)[0], ctx.tile_manager.get_tile_position(tile_id)[1]]}", "TILE_DATA_DEBUG")


def handle_tile_removed(ctx, item):
    build_new_player_output_flag = False  # Flag to know if at the end of this handler the player output needs to be resent

    tile_id = item.get("data").get("tile_id")
    tile_type = item.get("data").get("tile_type")

    ctx.tile_manager.update_tile(tile_id, tile_type)
    uhi_array = update_grid(ctx, tile_id)

    # If the removed tile is a player tile, update accordingly
    if tile_type > 6:
        ctx.player.remove_location(tile_id)
        last_locations = ctx.player.get_latest_location()
        if last_locations is not None:
            ctx.heatmap.set_spotlight(last_locations)
        else:
            ctx.heatmap.clear_spotlight()
        build_new_player_output_flag = True

    print(ctx.player.get_latest_location())
    # If a new player location is active, send this to unity and peripherals
    if build_new_player_output_flag:
        output = build_player_output(ctx.player.get_latest_location(), ctx.tile_manager, ctx.city, temperature, death)
        ctx.server_out.send_output(output)

    debug(f"Tile of type {tile_type} REMOVED at {tile_id}", "HANDLER_DEBUG")
    debug(f"UHI of new tile: {uhi_array[ctx.tile_manager.get_tile_position(tile_id)[0], ctx.tile_manager.get_tile_position(tile_id)[1]]}",  "TILE_DATA_DEBUG")


def handle_city_changed(ctx, item):
    city_id = item.get("data").get("city_id")
    ctx.city.update_city(city_id)
    ctx.heatmap.update_border(ctx.borders.get_border(ctx.city.name))

    debug(f"New city selected: {city_id}", "HANDLER_DEBUG")


def handle_time_changed(ctx, item):
    time = item.get("data").get("time")

    debug(f"New time selected: {time}", "HANDLER_DEBUG")
