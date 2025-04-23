import csv
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading


class CsvToJsonConverter:
    def __init__(self, root):
        # 初始化界面
        self.root = root
        self.root.title("CSV to JSON Converter")
        self.root.geometry("700x530")

        # 需要提取的字段
        self.requiredFields = ["name", "address_1", "state", "city",
                               "postal_code", "country", "gender",
                               "phone", "ssn", "ethnicity"]

        self.setupUI()

    def setupUI(self):
        """设置用户界面"""
        # 文件选择区域
        fileFrame = ttk.LabelFrame(self.root, text="选择CSV文件")
        fileFrame.pack(fill="x", padx=10, pady=10)

        self.fileListBox = tk.Listbox(fileFrame, height=10, width=80)
        self.fileListBox.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(fileFrame, orient="vertical", command=self.fileListBox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.fileListBox.config(yscrollcommand=scrollbar.set)

        # 按钮区域
        buttonFrame = ttk.Frame(self.root)
        buttonFrame.pack(fill="x", padx=10, pady=5)

        self.addFilesButton = ttk.Button(buttonFrame, text="添加文件", command=self.AddFiles)
        self.addFilesButton.pack(side=tk.LEFT, padx=5)

        self.clearFilesButton = ttk.Button(buttonFrame, text="清除文件", command=self.ClearFiles)
        self.clearFilesButton.pack(side=tk.LEFT, padx=5)

        # 输出区域
        outputFrame = ttk.LabelFrame(self.root, text="输出设置")
        outputFrame.pack(fill="x", padx=10, pady=10)

        ttk.Label(outputFrame, text="输出目录:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.outputPathVar = tk.StringVar()
        outputPathEntry = ttk.Entry(outputFrame, textvariable=self.outputPathVar, width=60)
        outputPathEntry.grid(row=0, column=1, padx=5, pady=5)

        browseButton = ttk.Button(outputFrame, text="浏览...", command=self.BrowseOutputDir)
        browseButton.grid(row=0, column=2, padx=5, pady=5)

        # 合并选项
        self.mergeFilesVar = tk.BooleanVar()
        self.mergeFilesVar.set(False)
        mergeCheckbox = ttk.Checkbutton(
            outputFrame,
            text="合并所有CSV到一个JSON文件",
            variable=self.mergeFilesVar
        )
        mergeCheckbox.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        ttk.Label(outputFrame, text="合并后的文件名:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.mergedFileNameVar = tk.StringVar()
        self.mergedFileNameVar.set("merged_data.json")
        mergedFileNameEntry = ttk.Entry(outputFrame, textvariable=self.mergedFileNameVar, width=60)
        mergedFileNameEntry.grid(row=2, column=1, padx=5, pady=5)

        # 进度区域
        progressFrame = ttk.LabelFrame(self.root, text="处理进度")
        progressFrame.pack(fill="x", padx=10, pady=10)

        self.progressBar = ttk.Progressbar(progressFrame, orient="horizontal", length=680, mode="determinate")
        self.progressBar.pack(padx=5, pady=5, fill="x")

        self.statusVar = tk.StringVar()
        self.statusVar.set("就绪")
        statusLabel = ttk.Label(progressFrame, textvariable=self.statusVar)
        statusLabel.pack(padx=5, pady=5)

        # 转换按钮
        self.convertButton = ttk.Button(self.root, text="开始转换", command=self.StartConversion)
        self.convertButton.pack(pady=20)

    def AddFiles(self):
        """添加CSV文件"""
        files = filedialog.askopenfilenames(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        for file in files:
            self.fileListBox.insert(tk.END, file)

    def ClearFiles(self):
        """清除文件列表"""
        self.fileListBox.delete(0, tk.END)

    def BrowseOutputDir(self):
        """选择输出目录"""
        outputDir = filedialog.askdirectory(title="选择输出目录")
        if outputDir:
            self.outputPathVar.set(outputDir)

    def ConvertCsvToJson(self, csvFiles, outputDir):
        """将CSV转换为JSON"""
        totalFiles = len(csvFiles)

        # 检查是否需要合并文件
        mergeFiles = self.mergeFilesVar.get()

        if mergeFiles:
            # 合并所有CSV数据到一个列表
            allJsonData = []

            for i, file in enumerate(csvFiles):
                try:
                    # 更新状态
                    fileName = os.path.basename(file)
                    self.statusVar.set(f"处理文件 {i + 1}/{totalFiles}: {fileName}")
                    self.progressBar["value"] = (i / totalFiles) * 100
                    self.root.update_idletasks()

                    with open(file, 'r', encoding='utf-8') as csvFile:
                        reader = csv.DictReader(csvFile)
                        for row in reader:
                            # 只提取需要的字段
                            filteredRow = {field: row.get(field, '') for field in self.requiredFields if field in row}
                            # 添加源文件信息
                            filteredRow["source_file"] = fileName
                            allJsonData.append(filteredRow)

                except Exception as e:
                    messagebox.showerror("错误", f"处理文件 {fileName} 时出错: {str(e)}")

            # 写入合并后的JSON文件
            mergedFileName = self.mergedFileNameVar.get()
            outputFile = os.path.join(outputDir, mergedFileName)

            try:
                with open(outputFile, 'w', encoding='utf-8') as jsonFile:
                    json.dump(allJsonData, jsonFile, indent=4, ensure_ascii=False)

                self.statusVar.set(f"已合并 {totalFiles} 个文件到 {mergedFileName}")
            except Exception as e:
                messagebox.showerror("错误", f"写入合并文件时出错: {str(e)}")

        else:
            # 分别处理每个文件
            for i, file in enumerate(csvFiles):
                try:
                    # 更新状态
                    fileName = os.path.basename(file)
                    self.statusVar.set(f"处理文件 {i + 1}/{totalFiles}: {fileName}")
                    self.progressBar["value"] = (i / totalFiles) * 100
                    self.root.update_idletasks()

                    jsonData = []
                    with open(file, 'r', encoding='utf-8') as csvFile:
                        reader = csv.DictReader(csvFile)
                        for row in reader:
                            # 只提取需要的字段
                            filteredRow = {field: row.get(field, '') for field in self.requiredFields if field in row}
                            jsonData.append(filteredRow)

                    # 创建输出文件名
                    baseName = os.path.splitext(fileName)[0]
                    outputFile = os.path.join(outputDir, f"{baseName}.json")

                    # 写入JSON文件
                    with open(outputFile, 'w', encoding='utf-8') as jsonFile:
                        json.dump(jsonData, jsonFile, indent=4, ensure_ascii=False)

                except Exception as e:
                    messagebox.showerror("错误", f"处理文件 {fileName} 时出错: {str(e)}")

        # 完成
        self.progressBar["value"] = 100
        self.statusVar.set("转换完成")
        messagebox.showinfo("完成", f"已成功转换 {totalFiles} 个文件")

    def StartConversion(self):
        """开始转换过程"""
        # 获取文件列表
        csvFiles = list(self.fileListBox.get(0, tk.END))
        if not csvFiles:
            messagebox.showwarning("警告", "请先选择CSV文件")
            return

        # 获取输出目录
        outputDir = self.outputPathVar.get()
        if not outputDir:
            messagebox.showwarning("警告", "请选择输出目录")
            return

        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        # 禁用按钮
        self.convertButton.config(state="disabled")
        self.addFilesButton.config(state="disabled")
        self.clearFilesButton.config(state="disabled")

        # 在后台线程中运行转换
        conversionThread = threading.Thread(
            target=lambda: self.ConvertCsvToJson(csvFiles, outputDir)
        )
        conversionThread.daemon = True
        conversionThread.start()

        # 设置任务完成后的回调
        self.CheckConversionStatus(conversionThread)

    def CheckConversionStatus(self, thread):
        """检查转换线程状态"""
        if thread.is_alive():
            # 如果线程仍在运行，稍后再检查
            self.root.after(100, lambda: self.CheckConversionStatus(thread))
        else:
            # 线程完成，重新启用按钮
            self.convertButton.config(state="normal")
            self.addFilesButton.config(state="normal")
            self.clearFilesButton.config(state="normal")


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = CsvToJsonConverter(root)
    root.mainloop()
