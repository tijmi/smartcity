from BuildOutput import build_player_output
import Info
from Helper_Functions import update_grid

# THIS HAS TO BE DONE DIFFERENTLY STILL, GET DATA FOR DEATHS AND TEMP
temperature = 0
death = 0


def handle_tile_placed(ctx, item):
    build_new_player_output_flag = False  # Flag to know if at the end of this handler the player output needs to be resent

    print(item)

    tile_id = item.get("data").get("tile_id")
    tile_type = item.get("data").get("tile_type_id")

    ctx.tile_manager.update_tile(tile_id, tile_type)
    uhi_array = update_grid(ctx, tile_id)

    # If the placed tile is a player tile, update accordingly
    if tile_type > 6:
        ctx.player.new_location(tile_id)
        ctx.heatmap.set_spotlight(ctx.player.get_latest_location())
        build_new_player_output_flag = True

    print(ctx.player.get_latest_location())
    # If a new player location is active, send this to unity and peripherals
    if build_new_player_output_flag:
        output = build_player_output(ctx.player.get_latest_location(), ctx.tile_manager, ctx.city, temperature, death)
        ctx.server_out.send_output(output)

    print("EVENT_DEBUG", f"{tile_type} tile PLACED at {tile_id}")
    print("NEW_TILE_UHI_DEBUG", f"UHI of new tile: {uhi_array[ctx.tile_manager.get_tile_position(tile_id)[0], ctx.tile_manager.get_tile_position(tile_id)[1]]}")


def handle_tile_removed(ctx, item):
    build_new_player_output_flag = False  # Flag to know if at the end of this handler the player output needs to be resent

    tile_id = item.get("data").get("tile_id")
    tile_type = item.get("data").get("tile_type_id")

    ctx.tile_manager.update_tile(tile_id, tile_type)
    uhi_array = update_grid(ctx, tile_id)

    # If the removed tile is a player tile, update accordingly
    if tile_type > 6:
        ctx.player.remove_location(tile_id)
        ctx.heatmap.set_spotlight(ctx.player.get_latest_location())
        build_new_player_output_flag = True

    print(ctx.player.get_latest_location())
    # If a new player location is active, send this to unity and peripherals
    if build_new_player_output_flag:
        output = build_player_output(ctx.player.get_latest_location(), ctx.tile_manager, ctx.city, temperature, death)
        ctx.server_out.send_output(output)

    print("EVENT_DEBUG", f"{tile_type} tile REMOVED at {tile_id}")
    print("NEW_TILE_UHI_DEBUG",
               f"UHI of new tile: {uhi_array[ctx.tile_manager.get_tile_position(tile_id)[0], ctx.tile_manager.get_tile_position(tile_id)[1]]}")

def handle_city_changed(ctx, item):
    print(item)
    city_id = item.get("data").get("city_id")
    ctx.city.update_city(city_id)
    ctx.heatmap.update_border(ctx.borders.get_border(ctx.city.name))

    print(f"new city received: {city_id}, {ctx.city.name}")


def handle_time_changed(ctx, item):
    time = item.get("data").get("time")

    # with open(Path(__file__).parent / "month_data.json", 'r') as jsonfile:
    #     month_data = json.load(jsonfile)
    #     temperature = month_data[str(month)]["temperature"]
    #     death = month_data[str(month)]["death"]