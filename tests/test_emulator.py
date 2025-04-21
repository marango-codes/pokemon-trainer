import pytest
import os

# Add project root to sys.path if necessary, or configure PYTHONPATH
# This assumes tests are run from the project root directory
from core.emulator import PokemonRedGameWrapper

# Use a real ROM path (replace with your actual ROM path)
# Ensure this ROM is accessible during testing
ROM_PATH = os.getenv("POKEMON_RED_ROM_PATH", "roms/pokemon_red.gb")

@pytest.fixture(scope="function")
def game_wrapper():
    """Pytest fixture to initialize the PokemonRedGameWrapper."""
    if not os.path.exists(ROM_PATH):
        pytest.skip(f"ROM file not found at {ROM_PATH}, skipping emulator tests.")

    # Use headless=True for testing
    wrapper = PokemonRedGameWrapper(rom_path=ROM_PATH, headless=True)
    yield wrapper
    wrapper.close() # Ensure emulator cleanup

def test_get_memory_value(game_wrapper):
    """Tests reading a single byte."""
    test_address = 0xC100 # Example RAM address
    expected_value = 0xAB
    game_wrapper.pyboy.memory[test_address] = expected_value
    assert game_wrapper.get_memory_value(test_address) == expected_value

def test_get_player_coords(game_wrapper):
    """Tests reading player X and Y coordinates."""
    expected_x = 10
    expected_y = 20
    # Constants defined in emulator: PLAYER_X_ADDR = 0xD361, PLAYER_Y_ADDR = 0xD362
    game_wrapper.pyboy.memory[game_wrapper.PLAYER_X_ADDR] = expected_x
    game_wrapper.pyboy.memory[game_wrapper.PLAYER_Y_ADDR] = expected_y
    assert game_wrapper.get_player_y() == expected_y # Checks memory[0xD362]
    assert game_wrapper.get_player_x() == expected_x # Checks memory[0xD361]
    assert game_wrapper.get_player_coords() == (expected_x, expected_y)

def test_get_current_map_id(game_wrapper):
    """Tests reading the current map ID."""
    expected_map_id = 12 # Pallet Town
    game_wrapper.pyboy.memory[game_wrapper.MAP_ID_ADDR] = expected_map_id
    assert game_wrapper.get_current_map_id() == expected_map_id

def test_get_party_count(game_wrapper):
    """Tests reading the party count."""
    expected_count = 3
    game_wrapper.pyboy.memory[game_wrapper.PARTY_COUNT_ADDR] = expected_count
    assert game_wrapper.get_party_count() == expected_count

def test_get_player_money(game_wrapper):
    """Tests reading and decoding player money."""
    # Set memory to represent $123456 in BCD
    game_wrapper.pyboy.memory[0xD347] = 0x12
    game_wrapper.pyboy.memory[0xD348] = 0x34
    game_wrapper.pyboy.memory[0xD349] = 0x56
    assert game_wrapper.get_player_money() == 123456

    # Test zero money
    game_wrapper.pyboy.memory[0xD347] = 0x00
    game_wrapper.pyboy.memory[0xD348] = 0x00
    game_wrapper.pyboy.memory[0xD349] = 0x00
    assert game_wrapper.get_player_money() == 0

    # Test max money (999999)
    game_wrapper.pyboy.memory[0xD347] = 0x99
    game_wrapper.pyboy.memory[0xD348] = 0x99
    game_wrapper.pyboy.memory[0xD349] = 0x99
    assert game_wrapper.get_player_money() == 999999

def test_get_rival_name(game_wrapper):
    """Tests reading the rival's name."""
    # Test case 1: Name "BLUE"
    name_blue_bytes = [0x81, 0x8B, 0x94, 0x84, 0x50] # B, L, U, E, Terminator
    for i, byte in enumerate(name_blue_bytes):
        game_wrapper.pyboy.memory[game_wrapper.RIVAL_NAME_ADDR + i] = byte
    # Clear remaining bytes in case of shorter names from previous tests
    for i in range(len(name_blue_bytes), 7):
         game_wrapper.pyboy.memory[game_wrapper.RIVAL_NAME_ADDR + i] = 0x00 # Fill unused slots
    assert game_wrapper.get_rival_name() == "BLUE"

    # Test case 2: Shorter name "RED"
    name_red_bytes = [0x91, 0x84, 0x83, 0x50] # R, E, D, Terminator
    for i, byte in enumerate(name_red_bytes):
        game_wrapper.pyboy.memory[game_wrapper.RIVAL_NAME_ADDR + i] = byte
    for i in range(len(name_red_bytes), 7):
         game_wrapper.pyboy.memory[game_wrapper.RIVAL_NAME_ADDR + i] = 0x00
    assert game_wrapper.get_rival_name() == "RED"

    # Test case 3: Max length name "GOLDBLU"
    name_goldblu_bytes = [0x86, 0x8E, 0x8B, 0x83, 0x81, 0x8B, 0x94, 0x50] # G, O, L, D, B, L, U, Terminator (Terminator at index 7)
    for i, byte in enumerate(name_goldblu_bytes):
         if i < 7: # Only write up to max length
            game_wrapper.pyboy.memory[game_wrapper.RIVAL_NAME_ADDR + i] = byte
    assert game_wrapper.get_rival_name() == "GOLDBLU"

def test_get_player_name(game_wrapper):
    """Tests reading the player's name."""
    # Test case 1: Name "ASH"
    name_ash_bytes = [0x80, 0x92, 0x87, 0x50] # A, S, H, Terminator
    for i, byte in enumerate(name_ash_bytes):
        game_wrapper.pyboy.memory[game_wrapper.PLAYER_NAME_ADDR + i] = byte
    # Clear remaining bytes
    for i in range(len(name_ash_bytes), 7):
         game_wrapper.pyboy.memory[game_wrapper.PLAYER_NAME_ADDR + i] = 0x00
    assert game_wrapper.get_player_name() == "ASH"

    # Test case 2: Max length name "TRAINER"
    name_trainer_bytes = [0x93, 0x91, 0x80, 0x88, 0x8D, 0x84, 0x91, 0x50] # T, R, A, I, N, E, R, Terminator
    for i, byte in enumerate(name_trainer_bytes):
        if i < 7:
            game_wrapper.pyboy.memory[game_wrapper.PLAYER_NAME_ADDR + i] = byte
    assert game_wrapper.get_player_name() == "TRAINER"

def test_get_badges(game_wrapper):
    """Tests reading the badge byte."""
    badge_addr = 0xD356

    # Test case 1: No badges (all bits 0)
    game_wrapper.pyboy.memory[badge_addr] = 0b00000000
    assert game_wrapper.get_badges() == 0

    # Test case 2: Boulder badge only (bit 0 set)
    game_wrapper.pyboy.memory[badge_addr] = 0b00000001
    assert game_wrapper.get_badges() == 1

    # Test case 3: Boulder and Cascade badges (bits 0 and 1 set)
    game_wrapper.pyboy.memory[badge_addr] = 0b00000011
    assert game_wrapper.get_badges() == 3

    # Test case 4: All badges (all bits 1)
    game_wrapper.pyboy.memory[badge_addr] = 0b11111111
    assert game_wrapper.get_badges() == 255

def test_get_pokedex_owned_count(game_wrapper):
    """Tests reading the Pokédex owned count."""
    lsb_addr = 0xD2F7
    msb_addr = 0xD2F8

    # Test case 1: Count = 0
    game_wrapper.pyboy.memory[lsb_addr] = 0
    game_wrapper.pyboy.memory[msb_addr] = 0
    assert game_wrapper.get_pokedex_owned_count() == 0

    # Test case 2: Count = 10 (0x0A)
    game_wrapper.pyboy.memory[lsb_addr] = 10
    game_wrapper.pyboy.memory[msb_addr] = 0
    assert game_wrapper.get_pokedex_owned_count() == 10

    # Test case 3: Count = 255 (0xFF)
    game_wrapper.pyboy.memory[lsb_addr] = 255
    game_wrapper.pyboy.memory[msb_addr] = 0
    assert game_wrapper.get_pokedex_owned_count() == 255

    # Test case 4: Count = 256 (0x0100)
    game_wrapper.pyboy.memory[lsb_addr] = 0
    game_wrapper.pyboy.memory[msb_addr] = 1
    assert game_wrapper.get_pokedex_owned_count() == 256

    # Test case 5: Count = 300 (0x012C)
    game_wrapper.pyboy.memory[lsb_addr] = 0x2C # 44
    game_wrapper.pyboy.memory[msb_addr] = 0x01 # 1
    assert game_wrapper.get_pokedex_owned_count() == 300

    # Test case 6: Max possible for 2 bytes = 65535 (0xFFFF)
    game_wrapper.pyboy.memory[lsb_addr] = 255
    game_wrapper.pyboy.memory[msb_addr] = 255
    assert game_wrapper.get_pokedex_owned_count() == 65535

def test_get_pokedex_seen_count(game_wrapper):
    """Tests reading the Pokédex seen count."""
    lsb_addr = 0xD30A
    msb_addr = 0xD30B

    # Test case 1: Count = 0
    game_wrapper.pyboy.memory[lsb_addr] = 0
    game_wrapper.pyboy.memory[msb_addr] = 0
    assert game_wrapper.get_pokedex_seen_count() == 0

    # Test case 2: Count = 15 (0x0F)
    game_wrapper.pyboy.memory[lsb_addr] = 15
    game_wrapper.pyboy.memory[msb_addr] = 0
    assert game_wrapper.get_pokedex_seen_count() == 15

    # Test case 3: Count = 255 (0xFF)
    game_wrapper.pyboy.memory[lsb_addr] = 255
    game_wrapper.pyboy.memory[msb_addr] = 0
    assert game_wrapper.get_pokedex_seen_count() == 255

    # Test case 4: Count = 256 (0x0100)
    game_wrapper.pyboy.memory[lsb_addr] = 0
    game_wrapper.pyboy.memory[msb_addr] = 1
    assert game_wrapper.get_pokedex_seen_count() == 256

    # Test case 5: Count = 400 (0x0190)
    game_wrapper.pyboy.memory[lsb_addr] = 0x90 # 144
    game_wrapper.pyboy.memory[msb_addr] = 0x01 # 1
    assert game_wrapper.get_pokedex_seen_count() == 400

    # Test case 6: Max possible for 2 bytes = 65535 (0xFFFF)
    game_wrapper.pyboy.memory[lsb_addr] = 255
    game_wrapper.pyboy.memory[msb_addr] = 255
    assert game_wrapper.get_pokedex_seen_count() == 65535

def test_get_time_played(game_wrapper):
    """Tests reading the time played assuming H:M:S:F in BCD."""
    h_addr = 0xDA40
    m_addr = 0xDA41
    s_addr = 0xDA42
    f_addr = 0xDA43 # Frames/Jiffies

    # Test case 1: 00:00:00:00
    game_wrapper.pyboy.memory[h_addr] = 0x00
    game_wrapper.pyboy.memory[m_addr] = 0x00
    game_wrapper.pyboy.memory[s_addr] = 0x00
    game_wrapper.pyboy.memory[f_addr] = 0x00
    assert game_wrapper.get_time_played() == (0, 0, 0, 0)

    # Test case 2: 01:23:45:59
    game_wrapper.pyboy.memory[h_addr] = 0x01
    game_wrapper.pyboy.memory[m_addr] = 0x23
    game_wrapper.pyboy.memory[s_addr] = 0x45
    game_wrapper.pyboy.memory[f_addr] = 0x59
    assert game_wrapper.get_time_played() == (1, 23, 45, 59)

    # Test case 3: 99:59:59:01 (Max hours/mins/secs BCD)
    game_wrapper.pyboy.memory[h_addr] = 0x99
    game_wrapper.pyboy.memory[m_addr] = 0x59
    game_wrapper.pyboy.memory[s_addr] = 0x59
    game_wrapper.pyboy.memory[f_addr] = 0x01
    assert game_wrapper.get_time_played() == (99, 59, 59, 1)

    # Test case 4: 10:05:08:30
    game_wrapper.pyboy.memory[h_addr] = 0x10
    game_wrapper.pyboy.memory[m_addr] = 0x05
    game_wrapper.pyboy.memory[s_addr] = 0x08
    game_wrapper.pyboy.memory[f_addr] = 0x30
    assert game_wrapper.get_time_played() == (10, 5, 8, 30)

def test_get_party_species(game_wrapper):
    """Tests reading the list of party Pokémon species IDs."""
    count_addr = 0xD163
    list_base_addr = 0xD164

    # Species IDs (example: Bulbasaur=153(0x99), Charmander=179(0xB3), Squirtle=177(0xB1))
    bulbasaur = 0x99
    charmander = 0xB3
    squirtle = 0xB1
    pidgey = 0x96
    rattata = 0xA5
    pikachu = 0x54
    terminator = 0xFF

    # Test case 1: Empty party
    game_wrapper.pyboy.memory[count_addr] = 0
    game_wrapper.pyboy.memory[list_base_addr] = terminator # Terminator should be present
    assert game_wrapper.get_party_species() == []

    # Test case 2: One Pokémon (Bulbasaur)
    game_wrapper.pyboy.memory[count_addr] = 1
    game_wrapper.pyboy.memory[list_base_addr + 0] = bulbasaur
    game_wrapper.pyboy.memory[list_base_addr + 1] = terminator
    assert game_wrapper.get_party_species() == [bulbasaur]

    # Test case 3: Three Pokémon (Bulbasaur, Charmander, Squirtle)
    game_wrapper.pyboy.memory[count_addr] = 3
    game_wrapper.pyboy.memory[list_base_addr + 0] = bulbasaur
    game_wrapper.pyboy.memory[list_base_addr + 1] = charmander
    game_wrapper.pyboy.memory[list_base_addr + 2] = squirtle
    game_wrapper.pyboy.memory[list_base_addr + 3] = terminator
    assert game_wrapper.get_party_species() == [bulbasaur, charmander, squirtle]

    # Test case 4: Full party (6 Pokémon)
    game_wrapper.pyboy.memory[count_addr] = 6
    party_6 = [bulbasaur, charmander, squirtle, pidgey, rattata, pikachu]
    for i, species_id in enumerate(party_6):
        game_wrapper.pyboy.memory[list_base_addr + i] = species_id
    game_wrapper.pyboy.memory[list_base_addr + 6] = terminator # Terminator should still be present
    assert game_wrapper.get_party_species() == party_6

    # Clean up memory
    game_wrapper.pyboy.memory[count_addr] = 0
    for i in range(7):
        game_wrapper.pyboy.memory[list_base_addr + i] = 0

def test_get_party_pokemon_nicknames(game_wrapper):
    """Test reading the nicknames of the party Pokémon."""
    # Manually set up the state for a single Pokémon (Bulbasaur)
    # because the default fixture state might not have a starter yet.

    # 1. Set party count to 1
    game_wrapper.pyboy.memory[game_wrapper.PARTY_COUNT_ADDR] = 1

    # 2. Set species ID for the first Pokémon (Bulbasaur = 0x01)
    # Although not strictly needed for nickname test, good practice for consistency
    game_wrapper.pyboy.memory[game_wrapper.PARTY_SPECIES_LIST_ADDR] = 0x01 # Corrected constant

    # 3. Write nickname "BULBASAUR" + terminator (0x50)
    nickname_bytes = [0x81, 0x94, 0x8B, 0x81, 0x80, 0x92, 0x80, 0x94, 0x91, 0x50] # BULBASAUR + terminator
    start_addr = game_wrapper.PARTY_NICKNAMES_ADDR
    for i, byte in enumerate(nickname_bytes):
        if i < game_wrapper.NICKNAME_LENGTH: # Ensure we don't write past max length
            game_wrapper.pyboy.memory[start_addr + i] = byte
    # Fill remaining bytes of the nickname slot with 0x00 (optional but clean)
    for i in range(len(nickname_bytes), game_wrapper.NICKNAME_LENGTH):
        game_wrapper.pyboy.memory[start_addr + i] = 0x00

    # Now, test the function
    nicknames = game_wrapper.get_party_pokemon_nicknames()
    assert isinstance(nicknames, list)
    assert len(nicknames) == 1, "Party should contain exactly one Pokémon after setup."
    assert nicknames[0] == "BULBASAUR", "The first nickname should be BULBASAUR."


def test_get_party_pokemon_data(game_wrapper):
    """Tests reading detailed data for party Pokémon."""
    party_count_addr = 0xD163
    pokemon1_addr = 0xD16B
    mem = game_wrapper.pyboy.memory

    # Test case 1: Empty party
    mem[party_count_addr] = 0
    assert game_wrapper.get_party_pokemon_data() == []

    # Test case 2: One Pokémon (Level 5 Bulbasaur example)
    mem[party_count_addr] = 1

    # Populate memory based on Data Crystal map (0xD16B onwards)
    bulbasaur_id = 0x99
    level = 5
    hp = 20
    max_hp = 20
    attack = 12
    defense = 13
    speed = 11
    special = 14
    status = 0 # No status
    type1 = 22 # Grass
    type2 = 3  # Poison
    move1 = 33 # Tackle
    move2 = 45 # Growl
    move3 = 0  # No move
    move4 = 0  # No move
    pp1 = 35
    pp2 = 40
    pp3 = 0
    pp4 = 0
    trainer_id = 12345 # Example ID
    exp = 125 # Exp for L5 medium slow
    hp_ev = 1000
    attack_ev = 1100
    defense_ev = 1200
    speed_ev = 1300
    special_ev = 1400
    # IVs: HP=5, Atk=10, Def=11, Spd=12, Spc=13 => 0xAB, 0xCD
    iv_byte1 = 0xAB
    iv_byte2 = 0xCD

    # Offsets relative to pokemon1_addr (0xD16B)
    mem[pokemon1_addr + 0x00] = bulbasaur_id
    write_little_endian(mem, pokemon1_addr + 0x01, hp, 2)
    # 0x03: Level (duplicate, ignore) - mem[pokemon1_addr + 0x03] = level
    mem[pokemon1_addr + 0x04] = status
    mem[pokemon1_addr + 0x05] = type1
    mem[pokemon1_addr + 0x06] = type2
    # 0x07: Catch rate (ignore) - mem[pokemon1_addr + 0x07] = 45 # Bulbasaur catch rate
    mem[pokemon1_addr + 0x08] = move1
    mem[pokemon1_addr + 0x09] = move2
    mem[pokemon1_addr + 0x0A] = move3
    mem[pokemon1_addr + 0x0B] = move4
    write_little_endian(mem, pokemon1_addr + 0x0C, trainer_id, 2)
    write_little_endian(mem, pokemon1_addr + 0x0E, exp, 3)
    write_little_endian(mem, pokemon1_addr + 0x11, hp_ev, 2)
    write_little_endian(mem, pokemon1_addr + 0x13, attack_ev, 2)
    write_little_endian(mem, pokemon1_addr + 0x15, defense_ev, 2)
    write_little_endian(mem, pokemon1_addr + 0x17, speed_ev, 2)
    write_little_endian(mem, pokemon1_addr + 0x19, special_ev, 2)
    mem[pokemon1_addr + 0x1B] = iv_byte1
    mem[pokemon1_addr + 0x1C] = iv_byte2
    mem[pokemon1_addr + 0x1D] = pp1
    mem[pokemon1_addr + 0x1E] = pp2
    mem[pokemon1_addr + 0x1F] = pp3
    mem[pokemon1_addr + 0x20] = pp4
    mem[pokemon1_addr + 0x21] = level # Actual level
    write_little_endian(mem, pokemon1_addr + 0x22, max_hp, 2)
    write_little_endian(mem, pokemon1_addr + 0x24, attack, 2)
    write_little_endian(mem, pokemon1_addr + 0x26, defense, 2)
    write_little_endian(mem, pokemon1_addr + 0x28, speed, 2)
    write_little_endian(mem, pokemon1_addr + 0x2A, special, 2)

    party_data = game_wrapper.get_party_pokemon_data()
    assert len(party_data) == 1
    p1_data = party_data[0]

    # Assertions
    assert p1_data['species_id'] == bulbasaur_id
    assert p1_data['current_hp'] == hp
    assert p1_data['level'] == level
    assert p1_data['status'] == status
    assert p1_data['type1'] == type1
    assert p1_data['type2'] == type2
    assert p1_data['moves'] == [move1, move2, move3, move4]
    assert p1_data['pp'] == [pp1, pp2, pp3, pp4]
    assert p1_data['trainer_id'] == trainer_id
    assert p1_data['exp'] == exp
    assert p1_data['evs'] == {'hp': hp_ev, 'attack': attack_ev, 'defense': defense_ev, 'speed': speed_ev, 'special': special_ev}
    assert p1_data['ivs'] == {'hp': 5, 'attack': 10, 'defense': 11, 'speed': 12, 'special': 13} # Calculated from 0xAB, 0xCD
    assert p1_data['stats'] == {'max_hp': max_hp, 'attack': attack, 'defense': defense, 'speed': speed, 'special': special}

    # Clean up (optional, as fixture handles game_wrapper teardown)
    mem[party_count_addr] = 0
    for i in range(44):
        mem[pokemon1_addr + i] = 0

# Helper to write little-endian values to PyBoy memory
def write_little_endian(mem, addr, value, num_bytes):
    for i in range(num_bytes):
        mem[addr + i] = (value >> (8 * i)) & 0xFF
