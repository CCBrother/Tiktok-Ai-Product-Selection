const PRODUCT_NAME_TRANSLATIONS: Record<string, string> = {
  "Magnetic Phone Cooling Grip": "磁吸手机散热手柄",
  "Pet Hair Detailer Glove": "宠物毛发清洁手套",
  "Under Desk Walking Pad Remote Holder": "桌下走步机遥控器收纳架",
  "Heatless Curling Travel Kit": "免热卷发旅行套装",
  "Reusable Lint Trap Bags": "可重复使用洗衣绒毛过滤袋",
  "Car Seat Gap Organizer Mini Vacuum": "车座缝隙收纳迷你吸尘器",
  "Clip-on Reading Light Bookmark": "夹式阅读灯书签",
  "Silicone Air Fryer Divider": "硅胶空气炸锅分隔垫",
  "Posture Reminder Necklace": "姿态提醒项链",
  "Portable Ice Roller Stick": "便携冰敷滚轮棒",
  "Cordless Mini Heat Sealer": "无线迷你封口机",
  "Laundry Scent Bead Measuring Cap": "洗衣香珠计量盖",
  "Kids Snack Spinner Tray": "儿童旋转零食盘",
  "Magnetic Stove Gap Cover": "磁吸炉灶缝隙挡条",
  "LED Purse Organizer Insert": "LED手袋收纳内胆",
  "Shower Foot Scrubber Mat": "淋浴足部清洁垫",
  "Portable Espresso Puck Screen Kit": "便携意式咖啡粉饼滤片套装",
  "Magnetic Cable Label Clips": "磁吸线缆标签夹",
  "No-Drill Curtain Rod Brackets": "免打孔窗帘杆支架",
  "Foldable Makeup Brush Drying Rack": "折叠化妆刷晾干架",
  "Reusable Produce Saver Discs": "可重复使用果蔬保鲜片",
  "Pet Nail Scratch Board": "宠物磨甲板",
  "Travel Jewelry Clasp Helper": "旅行首饰扣辅助器",
  "Mini Fridge Can Organizer Spring": "迷你冰箱饮料弹簧收纳架",
  "Portable Mini Blender": "便携迷你榨汁杯"
};

export function translateProductName(productName: string): string {
  return PRODUCT_NAME_TRANSLATIONS[productName] || "";
}

export function formatProductName(productName: string): string {
  const translation = translateProductName(productName);
  return translation ? `${productName}（${translation}）` : productName;
}

export function productImagePath(productName: string): string {
  const slug = productName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
  return `/product-images/${slug}.svg`;
}
