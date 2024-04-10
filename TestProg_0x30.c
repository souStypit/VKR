/***********************************************************
*  ÒÅÑÒ ÏĞÎÃĞÀÌÌÈĞÎÂÀÍÈß ÏÇÓ
***********************************************************/

// ÂÍÅØÍÈÉ ÌÅÕÀÍÈÇÌ ÇÀÙÈÒÛ ÑÅÊÒÎĞÎÂ, ÊÎÃÄÀ ÇÀÊĞÛÒÀ ÈÄÅÍÒÈÔÈÊÀÖÈß
//#define EXTERNAL_PROTECT  0
#define EXTERNAL_PROTECT 1

// #define DEBUG_
#ifdef DEBUG_
void print_rom_state(unsigned int *sector_address_ptr) {
    printf("\n  (%08X - %08X): %08X %08X %08X %08X", 
           sector_address_ptr, sector_address_ptr + 3, 
           sector_address_ptr[0], 
           sector_address_ptr[1], 
           sector_address_ptr[2], 
           sector_address_ptr[3]);
}
#endif
    
unsigned int main(/*int suspend, int sector_number*/)
{
    unsigned int sector_address;
    unsigned int _state = 0x0, delay_ressys = 305 /* ~ 9 ìêñ */;
    unsigned int sector_number = 4, suspend = 0x100000; // main parameters

    printf("\n\n  ÒÅÑÒ ÑÒÈĞÀÍÈß ÑÅÊÒÎĞÀ ÏÇÓ %d", sector_number);

    sector_address = get_sector_address(sector_number);
    printf("\n  Àäğåñ ñåêòîğà: %08X", sector_address);

    if (check_erase(sector_address)) erase(sector_address);

    program(sector_address, 0x01234567); // Ñòèğàíèå äëÿ êîğğåêòíîãî èñïîëíåíèÿ öèêëà
#ifdef DEBUG_
    print_rom_state((unsigned int *)sector_address);
#endif

    _state = erase_suspend(sector_address, suspend, delay_ressys);

    return _state;

}
