/***********************************************************
*  prog_rom.h
*  ÏĞÎÃĞÀÌÌÀÒÎĞ ÏÇÓ 
***********************************************************/
#ifndef _PROG_ROM_H__
#define _PROG_ROM_H__

#include "idtcpu.h"
#include "mcp.h"

__inline void wbflush (void) {asm("  sync");}
#define  WriteReg(addr,val) (*(volatile unsigned*)(K1BASE+(addr))=val/*,wbflush()*/)
#define  ReadReg(addr) (*(volatile unsigned*)(K1BASE+(addr)))

unsigned int R = 0; 			//   R - ñşäà çàïèñûâàåòñÿ ñîäåğæèìîå ğåãèñòğà
unsigned int RWR = 0;			// RWR - 	(1) - ïğîãğàììèğîâàíèå ğàçğåøåíî 
								//			(0) - çàïğåùåíî		

#define  RomManufacturerID     0x00010001  // ÈÇÃÎÒÎÂÈÒÅËÜ ÏÇÓ
#define  RomDeviceID           0x225B225B  // ÒÈÏ ÏÇÓ AM29LV800BB
#define  MaxRomSector                  19  // ÊÎËÈ×ÅÑÒÂÎ ÑÅÊÒÎĞÎÂ ÏÇÓ
#define  NumberOfProtectedSectors       4
#define  MaxRomChip                     2  // ÊÎËÈ×ÅÑÒÂÎ ÃĞÓÏÏ ÌÈÊĞÎÑÕÅÌ ÏÇÓ
#define  RomChipSize             0x200000  // ĞÀÇÌÅĞ ÏÇÓ
#define  MinRomSectorSize          0x4000  // ĞÀÇÌÅĞ ÍÀÈÌÅÍÜØÅÃÎ ÑÅÊÒÎĞÀ
#define  RomSize0                  0x8000  // ĞÀÇÌÅĞ ÑÅÊÒÎĞÀ 0
#define  RomSize1                  0x4000  // ĞÀÇÌÅĞ ÑÅÊÒÎĞÀ 1
#define  RomSize2                  0x4000  // ĞÀÇÌÅĞ ÑÅÊÒÎĞÀ 2
#define  RomSize3                 0x10000  // ĞÀÇÌÅĞ ÑÅÊÒÎĞÀ 3
#define  RomSize4                 0x20000  // ĞÀÇÌÅĞ ÑÅÊÒÎĞÀ 4 - 18

#define SHIFT 						   16

// DATA_AND_ADDR_BITS
#define b18 0x40000	//
#define b17 0x20000	// ONLY_ADDR_BITS
#define b16 0x10000	//

#define b15 0x8000
#define b14 0x4000
#define b13 0x2000
#define b12 0x1000
#define b11 0x800
#define b10 0x400
#define b9 	0x200
#define b8 	0x100
#define b7 	0x80	// DQ7
#define b6 	0x40	// DQ6 toggle
#define b5 	0x20	// DQ5				// DQ2 - PZU 2 
#define b4 	0x10						// DQ3 - PZU 2 
#define b3 	0x8		// DQ3
#define b2 	0x4		// DQ2 toggle		// DQ5 - PZU 2 
#define b1 	0x2							// DQ6 - PZU 2 
#define b0 	0x1							// DQ7 - PZU 2 

const unsigned int etalon_addresses[] = {
	ROM_BASE, 								    // Sector 0 
    ROM_BASE + RomSize0, 						// Sector 1
    ROM_BASE + RomSize0 + RomSize1, 			// Sector 2
    ROM_BASE + RomSize0 + RomSize1 + RomSize2, 	// Sector 3
    ROM_BASE + RomSize4                         // Sector 4 - 18
};

// Ğàáîòà ñ ñåêòîğàìè
unsigned int protected_sector(unsigned int sector_number);
unsigned int get_sector_address_raw(unsigned int sector_number);
unsigned int get_sector_address(unsigned int sector_number);

// Ğàçğåøåíèå ñòèğàíèÿ
void rwr_enable();
void rwr_disable();

// Ğàáîòà ñ ğàçíûìè áàíêàìè ÏÇÓ
unsigned int decode_data(unsigned int data);
unsigned int decode_addr(unsigned int addr);
void decode_sequence(unsigned int (*p_sAddr)[], unsigned int (*p_sData)[], unsigned int size);
void write_sequence(unsigned int *pAddr, unsigned int p_sAddr[], unsigned int p_sData[], unsigned int size);

// Ïğîãğàììèğîâàíèå
void algorithm_ub(unsigned int Addr);
void algorithm_ub_reset(unsigned int Addr);
void algorithm_ub_program(unsigned int Addr);
void algorithm_program(unsigned int Addr);
void program(unsigned int Addr, unsigned int data);

// Ñòèğàíèå
unsigned int check_erase(unsigned int Addr);
unsigned int read_pzu_data(unsigned int sector_addr, unsigned int delay_ressys);
void algorithm_sector_erase(unsigned int Addr);
void algorithm_sector_erase_suspend(unsigned int Addr, unsigned int delay);
void erase(unsigned int Addr);
unsigned int erase_suspend(unsigned int Addr, unsigned int delay_sus, unsigned int delay_ressys);

// ÒÀÉÌÅĞ
void wait_delay(const int delay);

#endif /* _PROG_ROM_H__ */
