#include "EncryptionHandler.h"

EncryptionHandler::EncryptionHandler()
{
	CryptoPP::AutoSeededRandomPool rng;
	private_key.GenerateRandomWithKeySize(rng, 2048);
	public_key = CryptoPP::RSA::PublicKey(private_key);
}


std::string EncryptionHandler::get_private_key() const
{
	std::string privateKey;
	CryptoPP::Base64Encoder encoder(nullptr, false);
	private_key.DEREncode(encoder);
	encoder.MessageEnd();
	CryptoPP::word64 size = encoder.MaxRetrievable();
	if (size)
	{
		privateKey.resize(size);
		encoder.Get(reinterpret_cast<unsigned char*>(&privateKey[0]), privateKey.size());
	}
	return privateKey;
}

std::string EncryptionHandler::get_public_key() const
{
	std::string publicKey;
	CryptoPP::Base64Encoder encoder(nullptr, false);
	public_key.DEREncode(encoder);
	encoder.MessageEnd();
	CryptoPP::word64 size = encoder.MaxRetrievable();
	if (size)
	{
		publicKey.resize(size);
		encoder.Get(reinterpret_cast<unsigned char*>(&publicKey[0]), publicKey.size());
	}
	return publicKey;
}

std::string EncryptionHandler::decrypt_AES_key_with_private_RSA_key(const std::string& encrypted_aes_key, const std::string& private_RSA)
{

	// Decode the base64-encoded encrypted AES key
	std::string decoded_aes_key;
	CryptoPP::StringSource ss(encrypted_aes_key, true,
		new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decoded_aes_key)));

	// Decrypt the AES key with the private RSA key
	CryptoPP::RSA::PrivateKey private_key = string_to_private_key(private_RSA);
	std::string decrypted_aes_key;
	CryptoPP::RSAES_OAEP_SHA_Decryptor decryptor(private_key);
	CryptoPP::AutoSeededRandomPool rng;
	CryptoPP::StringSource(decoded_aes_key, true,
		new CryptoPP::PK_DecryptorFilter(rng, decryptor,
			new CryptoPP::StringSink(decrypted_aes_key)));


	return decrypted_aes_key;
}

CryptoPP::RSA::PrivateKey EncryptionHandler::string_to_private_key(const std::string& private_key_str) {
	CryptoPP::RSA::PrivateKey privateKey;

	try {
		std::string decodedPrivateKey;
		CryptoPP::StringSource stringSource(private_key_str, true, new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decodedPrivateKey)));

		CryptoPP::ByteQueue byteQueue;
		byteQueue.Put(reinterpret_cast<const unsigned char*>(decodedPrivateKey.data()), decodedPrivateKey.size());

		privateKey.Load(byteQueue);
	}
	catch (const std::exception& ex) {
		std::cerr << "Error decoding private key: " << ex.what() << std::endl;
		throw; // rethrow the exception for the caller to handle
	}

	return privateKey;
}


CryptoPP::SecByteBlock EncryptionHandler::decodeBase64Key(const std::string& aes_key_base64) {
	std::string aes_key_binary;
	CryptoPP::StringSource(aes_key_base64, true,
		new CryptoPP::Base64Decoder(
			new CryptoPP::StringSink(aes_key_binary)));

	return CryptoPP::SecByteBlock((const CryptoPP::byte*)aes_key_binary.data(), CryptoPP::AES::BLOCKSIZE);
}

std::string EncryptionHandler::encryptFile(const std::string& filename, const CryptoPP::SecByteBlock& key) {
    // Step 1: Read the file to be encrypted
    std::ifstream input_file(filename, std::ios::binary);
    std::string plaintext((std::istreambuf_iterator<char>(input_file)),
        std::istreambuf_iterator<char>());

    CryptoPP::SecByteBlock iv(CryptoPP::AES::BLOCKSIZE);


    CryptoPP::CBC_Mode<CryptoPP::AES>::Encryption encryptor(key, key.size(), iv);

    // Step 2: Encrypt the file
    std::string ciphertext;
    CryptoPP::StringSource s(plaintext, true,
        new CryptoPP::StreamTransformationFilter(encryptor,
            new CryptoPP::StringSink(ciphertext)));


    return std::string(iv.begin(), iv.end()) + ciphertext;
}

std::string EncryptionHandler::parivate_key_to_string(const CryptoPP::RSA::PrivateKey& private_key)
{
	std::stringstream stream;
	CryptoPP::Base64Encoder encoder(nullptr, false);

	private_key.DEREncode(encoder);
	encoder.MessageEnd();

	CryptoPP::byte* buffer = new CryptoPP::byte[encoder.MaxRetrievable()];
	encoder.Get(buffer, encoder.MaxRetrievable());

	stream << std::string(reinterpret_cast<const char*>(buffer), encoder.MaxRetrievable());

	delete[] buffer;

	return stream.str();
}