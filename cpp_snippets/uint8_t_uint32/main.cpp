#include <iostream>
#include <iomanip>
#include <cstdint>
#include <memory>

inline void show_me(const std::string& name, void *arr) {

	std::cout << name << " ->" << std::endl;
	for (int i = 0; i < 8; i++) {

		std::cout 
			<< std::setw(15) << "uint8_t :" 
			<< std::setw(6) << (int)*(((uint8_t *)arr) + 4*i) << ' '
			<< std::setw(6) << (int)*(((uint8_t *)arr) + 4*i + 1) << ' '
			<< std::setw(6) << (int)*(((uint8_t *)arr) + 4*i + 2) << ' '
			<< std::setw(6) << (int)*(((uint8_t *)arr) + 4*i + 3) << ' '
			<< std::setw(15) << "uint32_t :"
			<< std::setw(12) << (int)*(((uint32_t *)arr) + i) << ' '
			<< std::endl;	
	}
}

int main() {

	class uint8TOuint32 {

		public:
			std::unique_ptr<uint32_t[]> val;
			uint8TOuint32(uint8_t *inp, int len) {
				val = std::unique_ptr<uint32_t[]> (new uint32_t[len]);
				for (int i = 0; i < len; i++) {
					val[i] = (uint32_t)inp[i];
				}
			}
			~uint8TOuint32() {};
	};

	std::cout << "uint8 to uint32 test" << std::endl;

	uint8_t byte_arr[] = {1, 2, 3, 4, 5, 6, 7, 8};
	show_me("byte_arr", (void*)byte_arr);

	uint8TOuint32 int_arr(byte_arr, 8);
	show_me("int_arr", (void*)int_arr.val.get());

	return 0;
}

