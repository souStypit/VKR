/***********************************************************
*  ������������ ��� 
***********************************************************/

#include "prog_rom.h"

// ������� ������ �������� ����������� �������
void set_zero_timer(void) 
{
    asm(".set noreorder; mtc0  $0,$9; nop; nop; .set reorder");
}
//----------//----------//----------//----------//----------//----------//----------//----------//----------//
// ������� ������ �������� ����������� �������
unsigned get_tick_timer(void) 
{
    asm(".set noreorder; mfc0  $2,$9; nop; nop; .set reorder");
}

unsigned int protected_sector(unsigned int sector_number) { return sector_number % MaxRomSector < NumberOfProtectedSectors; }

// ��������� ������ ������� �� ��� ������ ��� ����� K1BASE � ����� ���
unsigned int get_sector_address_raw(unsigned int sector_number) {
	return (protected_sector(sector_number)) ? 	etalon_addresses[sector_number] : // ���� ����������, �� ����� ����� �� etalon_address
												etalon_addresses[4] + RomSize4 * (sector_number - NumberOfProtectedSectors);
}

// ��������� ������ ������� �� ��� ������ � ������ K1BASE � ����� ���
unsigned int get_sector_address(unsigned int sector_number) {
	unsigned int num = sector_number % MaxRomSector;
	return K1BASE + (sector_number >= MaxRomSector ? RomChipSize : 0) + get_sector_address_raw(num);
}

// ���������� ���������������� ���
void rwr_enable() {							
	R = ReadReg(R_SYS);
	WriteReg(R_SYS, R | R_SYS_RWRROM);
	wbflush();
	RWR = 1;
}

// ���������� ���������������� ���
void rwr_disable() {			
	if (RWR) {	// �������� ��� ����, ����� �� ���� ������, ����� R ��� �� ��� �������� (�.�. ���������������� �� ���� ���������)
		WriteReg(R_SYS, R);
		wbflush();
		RWR = 0;
	}
}

unsigned int decode_data(unsigned int data) {
	unsigned int res = 0, tmp = 0;
	unsigned int i;

	for (i = 0; i < 2; i++) {
		if (data & b15) tmp |= b15;
		if (data & b14) tmp |= b8;
		if (data & b13) tmp |= b9;
		if (data & b12) tmp |= b10;
		if (data & b11) tmp |= b11;
		if (data & b10) tmp |= b12;
		if (data & b9) 	tmp |= b13;
		if (data & b8) 	tmp |= b14;
		if (data & b7) 	tmp |= b0;
		if (data & b6) 	tmp |= b1;
		if (data & b5) 	tmp |= b2;
		if (data & b4) 	tmp |= b3;
		if (data & b3) 	tmp |= b4;
		if (data & b2) 	tmp |= b5;
		if (data & b1) 	tmp |= b6;
		if (data & b0) 	tmp |= b7;
		data = data >> SHIFT;			// 1 ��. - ������� ������ �������� ����� 
		res |= i ? tmp : tmp << SHIFT;	// 2 ��. - ������� ������ �������� �����
	}
	
	return res;
}

unsigned int decode_addr(unsigned int addr) {
	unsigned int res = addr & 0x7F01F; // 0x7F01F ��� ������������ ������ ����� ������

	if (addr & b11) res |= b5;
	if (addr & b10) res |= b6;
	if (addr & b9) 	res |= b7;
	if (addr & b8) 	res |= b8;
	if (addr & b7) 	res |= b9;
	if (addr & b6) 	res |= b10;
	if (addr & b5) 	res |= b11;

	return res;
}

/*
	������������� ���� ������������������ ������� 
	(����� �� ������������ � ������ ������ ���� ������������������ � ���)
*/
void decode_sequence(unsigned int (*p_sAddr)[], unsigned int (*p_sData)[], unsigned int size) {
	unsigned int i, *s_addr, *s_data;
	s_addr = *p_sAddr;
	s_data = *p_sData;

	for (i = 0; i < size; i++) s_addr[i] = decode_addr(s_addr[i]);
	for (i = 0; i < size; i++) s_data[i] = decode_data(s_data[i]);
}

// ������ ������������������ � ���
void write_sequence(unsigned int *pAddr, unsigned int p_sAddr[], unsigned int p_sData[], unsigned int size) {
	unsigned int i;

	for (i = 0; i < size; i++) pAddr[p_sAddr[i]] = p_sData[i];
}

unsigned int check_erase(unsigned int Addr) {
	unsigned int i;
	unsigned int *pAddr = (unsigned int *)Addr;

	for (i = 0; i < RomSize4 >> 2 && i < ROM_SIZE >> 2; i++)
		if (pAddr[i] != 0xFFFFFFFF) return 1;	// ���� �� �����

	return 0;
}

void algorithm_ub(unsigned int Addr) {
#define sequence_size 4
	unsigned int s_data[sequence_size], s_addr[sequence_size];
	unsigned int *pAddr = (unsigned int *)Addr;

	s_addr[0] = 0x0;
	s_addr[1] = 0x555;
	s_addr[2] = 0x2AA;
	s_addr[3] = 0x555;
	s_data[0] = 0x000F000F;
	s_data[1] = 0x00AA00AA;
	s_data[2] = 0x00550055;
	s_data[3] = 0x00200020;

	if (Addr & RomChipSize) decode_sequence(&s_addr, &s_data, sequence_size);
	write_sequence(pAddr, s_addr, s_data, sequence_size);
#undef sequence_size
}

void algorithm_ub_reset(unsigned int Addr) {
#define sequence_size 2
	unsigned int s_data[sequence_size], s_addr[sequence_size];
	unsigned int *pAddr = (unsigned int *)Addr;

	s_addr[0] = 0x0;
	s_addr[1] = 0x0;
	s_data[0] = 0x00900090;
	s_data[1] = 0x00000000;

	if (Addr & RomChipSize) decode_sequence(&s_addr, &s_data, sequence_size);
	write_sequence(pAddr, s_addr, s_data, sequence_size);
#undef sequence_size
}

void algorithm_ub_program(unsigned int Addr) {
#define sequence_size 1
	unsigned int s_data[sequence_size], s_addr[sequence_size];
	unsigned int *pAddr = (unsigned int *)Addr;

	s_addr[0] = 0x0;
	s_data[0] = 0x00A000A0;

	if (Addr & RomChipSize) decode_sequence(&s_addr, &s_data, sequence_size);
	write_sequence(pAddr, s_addr, s_data, sequence_size);
#undef sequence_size
}

void algorithm_program(unsigned int Addr) { 
#define sequence_size 4
	unsigned int s_data[sequence_size], s_addr[sequence_size];
	unsigned int *pAddr = (unsigned int *)Addr;

	s_addr[0] = 0x0;
	s_addr[1] = 0x555;
	s_addr[2] = 0x2AA;
	s_addr[3] = 0x555;
	s_data[0] = 0x000F000F;
	s_data[1] = 0x00AA00AA;
	s_data[2] = 0x00550055;
	s_data[3] = 0x00A000A0;

	if (Addr & RomChipSize) decode_sequence(&s_addr, &s_data, sequence_size);
	write_sequence(pAddr, s_addr, s_data, sequence_size);
#undef sequence_size
}

void program(unsigned int Addr, unsigned int data) {
	unsigned int wordCounter = 0;
	unsigned int *pAddr = (unsigned int *)Addr;

	rwr_enable();

    algorithm_ub(Addr);
	for (wordCounter = 0; 
         (unsigned int)&pAddr[wordCounter] < Addr + RomSize4;
         wordCounter++) 
    {			
		// algorithm_program(Addr);
        algorithm_ub_program(Addr);
		pAddr[wordCounter] = data;
		while (pAddr[wordCounter] != data) ;
    }
    algorithm_ub_reset(Addr);

    rwr_disable();
}

void algorithm_sector_erase(unsigned int Addr) {
#define sequence_size 7
	unsigned int s_data[sequence_size], s_addr[sequence_size];
	unsigned int *pAddr = (unsigned int *)Addr;

	s_addr[0] = 0x0;
	s_addr[1] = 0x555;
	s_addr[2] = 0x2AA;
	s_addr[3] = 0x555;
	s_addr[4] = 0x555;
	s_addr[5] = 0x2AA;
	s_addr[6] = 0x0;
	s_data[0] = 0x00F000F0;
	s_data[1] = 0x00AA00AA;
	s_data[2] = 0x00550055;
	s_data[3] = 0x00800080;
	s_data[4] = 0x00AA00AA;
	s_data[5] = 0x00550055;
	s_data[6] = 0x00300030;

	if (Addr & RomChipSize) decode_sequence(&s_addr, &s_data, sequence_size);
	write_sequence(pAddr, s_addr, s_data, sequence_size);
#undef sequence_size
}

void algorithm_sector_erase_suspend(unsigned int Addr, unsigned int delay) {
	unsigned int *pAddr = (unsigned int *)Addr;

	algorithm_sector_erase(Addr);

	wbflush();
	wait_delay(delay * 75);

	if (Addr & RomChipSize) {
		pAddr[0] = 0x000D000D;  // SUSPEND
		pAddr[0] = 0x000F000F;	// �����
	} else {
		pAddr[0] = 0x00B000B0;
		pAddr[0] = 0x00F000F0;
	}
}

// ����� ������ ��� �������� ������ �����
// ������� ��������, �� �� ������
void erase(unsigned int Addr) {
	
	unsigned int *pAddr = (unsigned int *)Addr;

	rwr_enable();

	algorithm_sector_erase(Addr);

	while (pAddr[0] != 0xFFFFFFFF) ;

	while (check_erase(Addr)) ;

	rwr_disable();
}

void wait_delay(const int delay) {   
    int timer = 0;

    set_zero_timer(); 
    while (timer < delay) {
        timer = get_tick_timer();
    }
}

// ����� ������ ��� �������� ������ �����
// ������� ��������, �� �� ������
unsigned int read_pzu_data(unsigned int Addr, unsigned int delay_ressys) {
    unsigned int fstate = 0xFFFFFFFF; // ���-� ���������� ������������ �������� state
    // unsigned int state_set[4], state_mid[4], state_end[4]; // ��������� ��������� ��������� ������� ������� ���
    // unsigned int *sa_mid = (unsigned *)(Addr + 0x8000);  // �������� �������
    // unsigned int *sa_end = (unsigned *)(Addr + 0x1FFF0);  // �����
    // int K = 0, i = 0;
    
    unsigned Reg = ReadReg(R_SYS);       // ������ ���������� ��������
    WriteReg(R_SYS, Reg | R_SYS_RESSYS); // ����� ��� // ��� ��������������� �������� �� ��������
    wbflush();
    
    wait_delay(delay_ressys);
    
    WriteReg(R_SYS, Reg);                // ������ ������ ���
    wbflush();

    wait_delay(5);  // �������� ����� �������� ��� ����������� ������ ���
    
    // for (i = 0; i < 4; i++) { 
    //     fstate &= state_end[i] = sa_end[K + i];
    //     fstate &= state_mid[i] = sa_mid[K + i];
    //     fstate &= state_set[i] = Addr[K + i];
    // }
    
    // printf(
    //     "\n STATE: %08X"
    //     "\n {%8X-%8X} data\t0x%08X\t0x%08X\t0x%08X\t0x%08X" 
    //     "\n {%8X-%8X} data\t0x%08X\t0x%08X\t0x%08X\t0x%08X"
    //     "\n {%8X-%8X} data\t0x%08X\t0x%08X\t0x%08X\t0x%08X",
    //     fstate,
    //     Addr+K,  Addr+K+3,    state_set[K], state_set[K+1], state_set[K+2], state_set[K+3], 
    //     sa_mid+K,       sa_mid+K+3,         state_mid[K], state_mid[K+1], state_mid[K+2], state_mid[K+3], 
    //     sa_end+K,       sa_end+K+3,         state_end[K], state_end[K+1], state_end[K+2], state_end[K+3]); 
    
    return fstate; // �������� ���������
}

unsigned int erase_suspend(unsigned int Addr, unsigned int delay_sus, unsigned int delay_ressys) {
    int state = 0;
    rwr_enable();
    
	algorithm_sector_erase_suspend(Addr, delay_sus);
    
	rwr_disable();

    state = read_pzu_data(Addr, delay_ressys);
    
	return state;
}

/************************ ����� ������*********************/
