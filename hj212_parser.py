class HJ212Parser:
    def is_valid_message(self, message: str) -> bool:
        """检查报文格式是否正确：## + 4位长度 + 数据段 + 4位CRC + \r\n"""
        if not message.endswith("\r\n"):
            return False
        if not message.startswith("##"):
            return False
        if len(message) < 2 + 4 + 4 + 2:
            return False
        try:
            int(message[2:6])
        except ValueError:
            return False
        return True

    def validate_crc(self, message: str) -> bool:
        """ANSI CRC16，初始0xFFFF，多项式0xA001，校验报文CRC"""
        if not self.is_valid_message(message):
            return False
        msg_body = message[2:-6]
        crc_str = message[-6:-2]
        try:
            crc_received = int(crc_str, 16)
        except ValueError:
            return False

        crc = 0xFFFF
        poly = 0xA001
        for b in msg_body.encode('ascii'):
            crc ^= b
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
        crc_calc = crc & 0xFFFF
        return crc_calc == crc_received

    def parse_data_segment(self, message: str) -> dict:
        """解析数据段，返回键值对字典"""
        if not self.is_valid_message(message):
            return {}
        data_segment = message[6:-6]
        result = {}
        pairs = data_segment.split(';')
        for p in pairs:
            if '=' in p:
                k, v = p.split('=', 1)
                result[k.strip()] = v.strip()
        return result

    def extract_monitoring_data(self, message: str) -> dict:
        """从CP字段提取监测因子数据"""
        data_dict = self.parse_data_segment(message)
        cp_str = data_dict.get("CP", "")
        monitor_data = {}
        if not cp_str:
            return monitor_data
        items = cp_str.split(',')
        for item in items:
            if '=' in item:
                k, v = item.split('=',1)
                monitor_data[k.strip()] = v.strip()
        return monitor_data


# 测试示例
if __name__ == "__main__":
    parser = HJ212Parser()
    test_msg = "##0024QN=1;CP=SO2=12.3,NO=45.6;0F8C\r\n"
    print("报文合法：", parser.is_valid_message(test_msg))
    print("CRC校验：", parser.validate_crc(test_msg))
    print("解析数据段：", parser.parse_data_segment(test_msg))
    print("监测因子：", parser.extract_monitoring_data(test_msg))
