import re
import sys
import json
import random
from PyQt6.QtWidgets import QApplication, QDialog
from gui import Ui_Form  # 这里的 Ui_MainWindow 是从设计文件中生成的类


class MyWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.func = MyFunction()
        self.ui = Ui_Form()  # 创建 UI 实例
        self.ui.setupUi(self)  # 设置 UI
        self.init_set()

    def init_set(self) -> None:
        """设置拖拽和题目以及初始化"""
        for i in range(1, 13):
            line_edit = getattr(self.ui, f"lineEdit_{i}", None)
            if line_edit:
                line_edit.setDragEnabled(True)
        for i in range(1, 5):
            word = getattr(self.ui, f"word_{i}", None)
            if word:
                word.setAcceptDrops(True)
                word.setMaxLength(1)
        self.ui.label.setText("")
        self.ui.btn_clear.clicked.connect(self.clear_line_edit)
        self.ui.btn.clicked.connect(self.submit_function)
        self.creat_test()

    def clear_line_edit(self) -> None:
        """重置按钮功能"""
        for i in range(2, 5):
            word = getattr(self.ui, f"word_{i}", None)
            if word: word.clear()

    def creat_test(self) -> None:
        """创建新的题目"""
        self.func.main()
        self.show_test()

    def show_test(self) -> None:
        """渲染题目"""
        self.ui.word_1.setText(self.func.answer_word[0])
        for i, word in enumerate(self.func.test):
            line_edit = getattr(self.ui, f"lineEdit_{i + 1}", None)
            if line_edit: line_edit.setText(word)

    def submit_function(self) -> None:
        """提交按钮功能"""
        submit_answer = ''.join([getattr(self.ui, f"word_{i}").text() for i in range(1, 5)])
        if submit_answer == self.func.answer_word:
            self.ui.label.setText(f'{self.func.answer_word}')
            self.ui.word_1.setText(f'{submit_answer[0]}')
            _re = self.func.create_next_test(submit_answer)
            if _re == 404:
                self.ui.label.setText(f'数据库中无"{submit_answer[3]}"开头的成语')
                self.creat_test()
                self.clear_line_edit()
            self.show_test()
            self.clear_line_edit()
        else:
            self.ui.label.setText(f'回答错误，正确答案是：{self.func.answer_word}')
            self.creat_test()
            self.clear_line_edit()


class MyFunction:
    def __init__(self):
        self.word_list = []
        self.answer_word = None
        self.test = None
        self.word_dict = None

        with open('data.json', 'r', encoding='utf-8') as f:
            # 从json中加载数据
            json_datas = json.load(f)
            self.word_list = [re.sub(r'[^\u4e00-\u9fa5]', '', json_data['word']) for json_data in json_datas]
            # 单词数据
        self.classify_first_word(self.word_list)

    def classify_first_word(self, data: list) -> None:
        """将成语分类"""
        word_dict = {}
        for i in data:
            if len(i) > 4:
                continue
            first_char = i[0]
            last_char = i[len(i) - 1]
            if first_char in word_dict.keys():
                word_dict[first_char].append(i)
                if last_char not in word_dict.keys():
                    word_dict[last_char] = []
            else:
                word_dict[first_char] = [i]
                if last_char not in word_dict.keys():
                    word_dict[last_char] = []

        filtered_data = {key: value for key, value in word_dict.items() if len(value) >= 5}
        self.word_dict = filtered_data

    @staticmethod
    def random_word(data: list[str]) -> str:
        """随机一个成语"""
        return random.choice(data)

    @staticmethod
    def create_test(data: list[str], word: str) -> list[str]:
        """制作题目"""
        all_words = ''.join(data)
        re_word_list = random.sample(all_words, 9)
        mylist = re_word_list + [i for i in word][1:]
        # random.shuffle(mylist)#打乱顺序
        return mylist

    def create_next_test(self, old_answer_word: str) -> int:
        if old_answer_word[3] not in self.word_dict.keys():
            return 404
        word_list = self.word_dict[old_answer_word[3]]
        answer_word = self.random_word(word_list)
        self.choose_word_and_test(answer_word)
        return 200

    def main(self) -> None:
        # 随机一个单词
        answer_word = self.random_word(self.word_list)
        self.choose_word_and_test(answer_word)

    def choose_word_and_test(self, answer_word: str) -> None:
        test = self.create_test(self.word_dict, answer_word)
        self.answer_word = answer_word
        self.test = test


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
